from celery import shared_task
from django.core.files.storage import default_storage
from .models import Document
from .utils import extract_text_from_pdf, create_text_chunks, generate_embeddings, store_document_chunks
import asyncio
import logging

# Set up a logger
logger = logging.getLogger(__name__)

@shared_task
def process_document(document_id: int) -> None:
    """Process a PDF document: extract text, create chunks, generate embeddings, and store in database."""
    return
    try:
        # Get the document object
        document = Document.objects.get(id=document_id)
        
        # Get the file path
        file_path = document.file.path
        
        # Extract text from PDF
        text = extract_text_from_pdf(file_path)
        
        # Create text chunks
        text_chunks = create_text_chunks(text)
        
        # Run async function (generate_embeddings) synchronously using asyncio
        embeddings = asyncio.run(generate_embeddings(text_chunks))  # Running async function in sync task
        
        # Store chunks and embeddings
        store_document_chunks(document, text_chunks, embeddings)
        
        # Mark document as processed
        document.processed = True
        document.save()
        
    except Document.DoesNotExist:
        logger.error(f"Document with id {document_id} does not exist")
    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}")
        raise
