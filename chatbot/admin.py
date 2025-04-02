from django.contrib import admin
from .models import ChatbotSession, ChatMessage

class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 1

@admin.register(ChatbotSession)
class ChatbotSessionAdmin(admin.ModelAdmin):
    list_display = ("chatbot", "session_id", "created_at", "last_active", "ip_address")
    search_fields = ("session_id", "chatbot__name")
    inlines = [ChatMessageInline]

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("session", "role", "content", "created_at")
    search_fields = ("session__session_id", "content")
