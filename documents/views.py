from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Document, Conversation, Message
from .serializers import DocumentSerializer, ConversationSerializer, MessageSerializer, ChatInputSerializer
from .tasks import process_document
from .utils import search_similar_chunks
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from django.conf import settings
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from django.views.decorators.clickjacking import xframe_options_exempt
from django.http import FileResponse, Http404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework.permissions import IsAuthenticated

class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        document = serializer.save()
        # Trigger async processing of the document
        Conversation.objects.create(document=document, user=document.user)   
        process_document.delay(document.id)

@xframe_options_exempt
@login_required
def serve_pdf(request, pk):
    try:
        document = Document.objects.get(pk=pk, user=request.user)
        return FileResponse(document.file.open('rb'), content_type='application/pdf')
    except Document.DoesNotExist:
        raise Http404("Document not found or you don't have permission.")
    

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'],serializer_class=ChatInputSerializer)
    def chat(self, request, pk=None):
        conversation = self.get_object()
        serializer = ChatInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        message_content = serializer.validated_data['message']
        
        # Save user message
        Message.objects.create(
            conversation=conversation,
            role='user',
            content=message_content
        )
        
        # Get relevant document chunks
        similar_chunks = search_similar_chunks(
            query=message_content,
            document=conversation.document,
            top_k=3
        )
        
        # Prepare conversation history
        messages = []
        system_prompt = (
            "You are a helpful AI assistant that answers questions about the document. "
            "Use the provided context to answer questions accurately. "
            "If you're unsure or the answer isn't in the context, say so."
        )
        messages.append(SystemMessage(content=system_prompt))
        
        # Add relevant context
        context = '\n\n'.join([chunk['content'] for chunk in similar_chunks])
        context_prompt = f"Context from the document:\n{context}"
        messages.append(SystemMessage(content=context_prompt))
        
        # Add conversation history (last 5 messages)
        history = conversation.messages.order_by('-created_at')[:5][::-1]
        for msg in history:
            if msg.role == 'user':
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == 'assistant':
                messages.append(AIMessage(content=msg.content))
        
        # Get response from NVIDIA AI Foundation Models
        try:
            chat = ChatNVIDIA(
                model='meta/llama3-8b-instruct',
                temperature=0.7,
                max_tokens=1024,
                base_url="https://integrate.api.nvidia.com/v1", 
                api_key=settings.NVIDIA_API_KEY 
            )
            response = chat(messages)
        except Exception as e:
            return Response({"error": f"AI API error: {str(e)}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
              

        
        # Save assistant message
        assistant_message = Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=response.content
        )
        
        return Response(MessageSerializer(assistant_message).data)