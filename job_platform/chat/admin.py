from django.contrib import admin
from .models import Chat, Message

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'participants_list', 'created_at')

    def participants_list(self, obj):
        return ", ".join([p.username for p in obj.participants.all()])
    participants_list.short_description = "Participants"

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'sender', 'created_at', 'text')
