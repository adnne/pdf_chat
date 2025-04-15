import os
import uuid
from typing import List, Dict, Any, TYPE_CHECKING
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from django.conf import settings

from .qdrant_client import qdrant_client, COLLECTION_NAME, models

if TYPE_CHECKING:
    from .models import DocumentChunk


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text content from a PDF file."""
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    return ''.join(page.page_content for page in pages)


def create_text_chunks(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """Split text into chunks using LangChain's text splitter."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=True,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    return splitter.split_text(text)


async def generate_embeddings(text_chunks: List[str]) -> List[List[float]]:
    """Generate embeddings for text chunks using NVIDIA's API in batch."""
    embeddings = NVIDIAEmbeddings(model="NV-Embed-QA", api_key=settings.NVIDIA_API_KEY)
    return await embeddings.aembed_documents(text_chunks)


def store_document_chunks(document, text_chunks: List[str], embeddings: List[List[float]]) -> None:
    """Store document chunks and their embeddings in Qdrant and PostgreSQL."""
    from .models import DocumentChunk  # runtime import to avoid circular import

    chunks = []
    points = []

    for i, (chunk, embedding) in enumerate(zip(text_chunks, embeddings)):
        vector_id = str(uuid.uuid4())

        points.append(models.PointStruct(
            id=vector_id,
            vector=embedding,
            payload={
                'document_id': document.id,
                'chunk_number': i,
                'content': chunk
            }
        ))

        chunks.append(DocumentChunk(
            document=document,
            content=chunk,
            chunk_number=i,
            vector_id=vector_id
        ))

    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

    DocumentChunk.objects.bulk_create(chunks)


def search_similar_chunks(query: str, document, top_k: int = 3) -> List[Dict[str, Any]]:
    """Search for similar chunks using Qdrant vector similarity search."""
    from .models import DocumentChunk  # runtime import to avoid circular import

    embeddings = NVIDIAEmbeddings(model="NV-Embed-QA", api_key=settings.NVIDIA_API_KEY)
    query_embedding = embeddings.embed_query(query)

    chunk_vector_ids = set(DocumentChunk.objects.filter(
        document=document
    ).values_list('vector_id', flat=True))

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
