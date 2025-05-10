# chat/views.py
from rest_framework import viewsets, permissions
from .models import Message
from .serializers import MessageSerializer
from rest_framework.response import Response
from rest_framework.decorators import action

class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(
            sender=user
        ) | Message.objects.filter(
            recipient=user
        )

    @action(detail=False, methods=['get'], url_path='between/(?P<user_id>\d+)')
    def messages_between(self, request, user_id=None):
        user = request.user
        messages = Message.objects.filter(
            (Q(sender=user, recipient__id=user_id) |
             Q(sender__id=user_id, recipient=user))
        ).order_by('timestamp')
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
