import os
import uuid
from typing import List, Dict, Any
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from django.conf import settings
from .qdrant_client import qdrant_client, COLLECTION_NAME, models

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text content from a PDF file."""
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    text = ''
    for page in pages:
        text += page.page_content
    return text

def create_text_chunks(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """Split text into chunks using LangChain's text splitter."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=True,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    return text_splitter.split_text(text)

async def generate_embeddings(text_chunks: List[str]) -> List[List[float]]:
    """Generate embeddings for text chunks using NVIDIA's API in batch."""
    embeddings = NVIDIAEmbeddings(model="NV-Embed-QA", api_key=settings.NVIDIA_API_KEY)
    return await embeddings.aembed_documents(text_chunks)

def store_document_chunks(document, text_chunks: List[str], embeddings: List[List[float]]) -> None:
    """Store document chunks and their embeddings in Qdrant and references in PostgreSQL."""
    chunks = []
    points = []
    
    for i, (chunk, embedding) in enumerate(zip(text_chunks, embeddings)):
        # Generate a unique ID for the vector
        vector_id = str(uuid.uuid4())
        
        # Create point for Qdrant
        points.append(models.PointStruct(
            id=vector_id,
            vector=embedding,
            payload={
                'document_id': document.id,
                'chunk_number': i,
                'content': chunk
            }
        ))
        
        # Create chunk object for PostgreSQL
        chunk_obj = DocumentChunk(
            document=document,
            content=chunk,
            chunk_number=i,
            vector_id=vector_id
        )
        chunks.append(chunk_obj)
    
    # Store vectors in Qdrant
    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )
    
    # Import DocumentChunk at runtime to avoid circular import
    from .models import DocumentChunk
    # Store chunk references in PostgreSQL
    DocumentChunk.objects.bulk_create(chunks)

def search_similar_chunks(query: str, document, top_k: int = 3) -> List[Dict[str, Any]]:
    """Search for similar chunks using Qdrant vector similarity search."""
    embeddings = NVIDIAEmbeddings(model="NV-Embed-QA", api_key=settings.NVIDIA_API_KEY)
    query_embedding = embeddings.embed_query(query)
    
    # Get document chunk vector_ids
    # Import DocumentChunk at runtime to avoid circular import
    from .models import DocumentChunk
    chunk_vector_ids = set(DocumentChunk.objects.filter(
        document=document
    ).values_list('vector_id', flat=True))
    
    # Search in Qdrant
    search_result = qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding,
        query_filter=models.Filter(
            must=[models.FieldCondition(
                key="document_id",
                match=models.MatchValue(value=document.id)
            )]
        ),
        limit=top_k
    )
    
    return [
        {
            'content': hit.payload['content'],
            'chunk_number': hit.payload['chunk_number'],
            'distance': hit.score
        }
        for hit in search_result
        if hit.id in chunk_vector_ids
    ]