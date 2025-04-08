from qdrant_client import QdrantClient
from qdrant_client.http import models
from django.conf import settings

# Initialize Qdrant client
qdrant_client = QdrantClient(url=settings.QDRANT_HOST)

# Collection name for document vectors
COLLECTION_NAME = "document_chunks"

# Create collection if it doesn't exist
try:
    qdrant_client.get_collection(COLLECTION_NAME)
except Exception:
    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=1024,  # NVIDIA NV-Embed-QA embedding size
            distance=models.Distance.COSINE
        )
    )