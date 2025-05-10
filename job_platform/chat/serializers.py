from rest_framework import serializers
from .models import Conversation, Message, Notification
from django.contrib.auth import get_user_model
from users.serializers import UserSerializer

User = get_user_model()


class MessageSerializer(serializers.ModelSerializer):
    sender_details = UserSerializer(source='sender', read_only=True)

    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'sender', 'sender_details',
            'content', 'timestamp', 'is_read'
        ]
        read_only_fields = ['id', 'timestamp', 'is_read', 'sender_details']


class ConversationSerializer(serializers.ModelSerializer):
    participants_details = UserSerializer(
        source='participants', many=True, read_only=True
    )
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id', 'participants', 'participants_details',
            'created_at', 'updated_at', 'is_active',
            'last_message', 'unread_count'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at',
            'last_message', 'unread_count'
        ]

    def get_last_message(self, obj):
        message = obj.messages.order_by('-timestamp').first()
        if message:
            return {
                'id': message.id,
                'sender': message.sender.id,
                'content': message.content,
                'timestamp': message.timestamp,
                'is_read': message.is_read,
            }
        return None

    def get_unread_count(self, obj):
        user = self.context.get('request').user
        return obj.messages.filter(is_read=False).exclude(sender=user).count()


class NotificationSerializer(serializers.ModelSerializer):
    message_details = MessageSerializer(source='message', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'conversation', 'message',
            'message_details', 'is_read', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'message_details']
