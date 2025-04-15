from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer

class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Показываем только чаты, в которых участвует текущий user
        user = self.request.user
        return Chat.objects.filter(participants=user)

    def perform_create(self, serializer):
        # При создании чата можем передавать список participants
        # Пример: participants = [2, 5]
        chat = serializer.save()
        participants_ids = self.request.data.get('participants', [])
        for pid in participants_ids:
            chat.participants.add(pid)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        chat = self.get_object()
        msgs = chat.messages.all()
        data = MessageSerializer(msgs, many=True).data
        return Response(data)
