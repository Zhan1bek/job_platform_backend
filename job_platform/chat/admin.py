from django.contrib import admin
from .models import Chat, Message

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'job_seeker', 'employer')
    search_fields = ('job_seeker__user__username', 'employer__user__username')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'sender', 'text_preview', 'timestamp', 'is_read')
    list_filter = ('is_read',)
    search_fields = ('sender__username', 'chat__job_seeker__user__username', 'chat__employer__user__username')

    def text_preview(self, obj):
        return obj.text[:50] + '...' if obj.text else "[Attachment]"
    text_preview.short_description = "Message Preview"
