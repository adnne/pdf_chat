from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .qdrant_client import qdrant_client, COLLECTION_NAME

User = get_user_model()

class Document(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(
        upload_to='documents/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')

    def __str__(self):
        return self.title

class DocumentChunk(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks')
    content = models.TextField()
    chunk_number = models.IntegerField()
    vector_id = models.CharField(max_length=255, null=True, blank=True)  # Store reference to vector in external vector DB
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['chunk_number']
        indexes = [
            models.Index(fields=['document', 'chunk_number']),
        ]

    def __str__(self):
        return f"{self.document.title} - Chunk {self.chunk_number}"

class Conversation(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='conversations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Conversation with {self.document.title}"

class Message(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


@receiver(pre_delete, sender=DocumentChunk)
def delete_vector_from_qdrant(sender, instance, **kwargs):
    """Delete the corresponding vector from Qdrant when a DocumentChunk is deleted."""
    if instance.vector_id:
        try:
            qdrant_client.delete(
                collection_name=COLLECTION_NAME,
                points_selector=[instance.vector_id]
            )
        except Exception as e:
            print(f"Error deleting vector from Qdrant: {e}")