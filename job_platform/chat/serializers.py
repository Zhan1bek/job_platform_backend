from rest_framework import serializers
from .models import Chat, Message

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'chat', 'text', 'attachment', 'timestamp', 'is_read', 'sender', 'sender_name']
        read_only_fields = ['sender', 'timestamp']


class ChatSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ['id', 'job_seeker', 'employer', 'last_message']

    def get_last_message(self, obj):
        last = obj.messages.order_by('-timestamp').first()
        if last:
            return {
                "text": last.text,
                "timestamp": last.timestamp,
                "sender": last.sender.username
            }
        return None