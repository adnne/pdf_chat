from django.contrib import admin
from .models import Document, DocumentChunk, Conversation, Message

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'uploaded_at', 'processed']
    list_filter = ['processed', 'uploaded_at']
    search_fields = ['title', 'user__username']
    readonly_fields = ['uploaded_at', 'processed']

@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ['document', 'chunk_number', 'created_at']
    list_filter = ['created_at']
    search_fields = ['document__title', 'content']
    readonly_fields = ['created_at']

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['document', 'user', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['document__title', 'user__username']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'role', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['conversation__document__title', 'content']
    readonly_fields = ['created_at']