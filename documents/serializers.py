from rest_framework import serializers
from .models import Document, DocumentChunk, Conversation, Message

class DocumentSerializer(serializers.ModelSerializer):
    conversation = serializers.IntegerField(source='conversation.id', read_only=True)
    class Meta:
        model = Document
        fields = ['id', 'title', 'file', 'uploaded_at', 'processed', 'user', 'file_size','conversation']
        read_only_fields = ['uploaded_at', 'processed', 'user']

    def create(self, validated_data):
        # Set the user from the request context
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class DocumentChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentChunk
        fields = ['id', 'document', 'content', 'chunk_number', 'created_at']
        read_only_fields = ['created_at']

class ChatInputSerializer(serializers.Serializer):
    message = serializers.CharField(required=True, max_length=2000)

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'role', 'content', 'created_at']
        read_only_fields = ['created_at']

class ChatOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['role', 'content', 'created_at']
        read_only_fields = ['role', 'content', 'created_at']

class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    document_title = serializers.CharField(source='document.title', read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'document', 'document_title', 'user', 'messages', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'user']

    def create(self, validated_data):
        # Set the user from the request context
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)