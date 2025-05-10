from django.contrib import admin
from .models import Conversation, Message, Notification


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    fields = ('sender', 'content', 'timestamp', 'is_read')
    readonly_fields = ('timestamp',)


class NotificationInline(admin.TabularInline):
    model = Notification
    extra = 0
    fields = ('user', 'message', 'is_seen', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_participants', 'created_at',
                    'updated_at', 'is_active', 'message_count')
    list_filter = ('is_active', 'created_at')
    search_fields = ('participants__username', 'participants__email')
    inlines = [MessageInline]
    filter_horizontal = ('participants',)

    def get_participants(self, obj):
        return ", ".join(user.username for user in obj.participants.all())
    get_participants.short_description = 'Участники'

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Количество сообщений'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender',
                    'short_content', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp', 'sender')
    search_fields = ('content', 'sender__username')
    readonly_fields = ('timestamp',)
    raw_id_fields = ('conversation', 'sender')
    inlines = [NotificationInline]

    def short_content(self, obj):
        return (obj.content[:50] + '...'
                if len(obj.content) > 50 else obj.content)
    short_content.short_description = 'Текст'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'message_preview',
                    'is_seen', 'created_at')
    list_filter = ('is_seen', 'created_at')
    search_fields = ('user__username', 'message__content')
    readonly_fields = ('created_at',)
    raw_id_fields = ('user', 'message')

    def message_preview(self, obj):
        text = obj.message.content
        return text[:30] + '...' if len(text) > 30 else text
    message_preview.short_description = 'Сообщение'
