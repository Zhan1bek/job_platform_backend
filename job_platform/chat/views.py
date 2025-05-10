from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .models import Conversation, Message, Notification
from .serializers import ConversationSerializer, MessageSerializer, NotificationSerializer
from .permissions import IsConversationParticipant
from users.serializers import UserSerializer

User = get_user_model()


# ──────────────────────────── Conversation ──────────────────────────── #

class ConversationViewSet(viewsets.ModelViewSet):
    """API для управления беседами"""
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Беседы, в которых участвует текущий пользователь"""
        return Conversation.objects.filter(participants=self.request.user)

    def get_permissions(self):
        if self.action in ['retrieve', 'messages', 'mark_as_read', 'send_message']:
            return [permissions.IsAuthenticated(), IsConversationParticipant()]
        return super().get_permissions()

    # ----- Доп. действия -----

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Все сообщения в беседе"""
        conversation = self.get_object()
        page = self.paginate_queryset(conversation.messages.all())
        if page is not None:
            serializer = MessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = MessageSerializer(conversation.messages.all(), many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Отправить сообщение"""
        conversation = self.get_object()
        serializer = MessageSerializer(data={
            'conversation': conversation.id,
            'sender': request.user.id,
            'content': request.data.get('content')
        })
        if serializer.is_valid():
            message = serializer.save()
            # создаём уведомления
            for participant in conversation.participants.exclude(id=request.user.id):
                Notification.objects.create(
                    user=participant,
                    conversation=conversation,
                    message=message
                )
            conversation.save()       # обновит updated_at
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Отметить сообщения как прочитанные"""
        conversation = self.get_object()
        Message.objects.filter(
            conversation=conversation,
            is_read=False
        ).exclude(sender=request.user).update(is_read=True)

        Notification.objects.filter(
            user=request.user,
            conversation=conversation,
            is_seen=False
        ).update(is_seen=True)

        return Response({'status': 'messages marked as read'})

    @action(detail=False, methods=['get'])
    def create_or_get_direct(self, request):
        """Создать или получить личную беседу с пользователем"""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        other_user = get_object_or_404(User, pk=user_id)
        conversation, _ = Conversation.get_or_create_conversation(request.user, other_user)
        serializer = ConversationSerializer(conversation, context={'request': request})
        return Response(serializer.data)


# ───────────────────────────── Messages ────────────────────────────── #

class MessageViewSet(viewsets.ModelViewSet):
    """API для управления сообщениями"""
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsConversationParticipant]

    def get_queryset(self):
        user_conversations = Conversation.objects.filter(participants=self.request.user)
        return Message.objects.filter(conversation__in=user_conversations)

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


# ─────────────────────────── Notifications ─────────────────────────── #

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """API для уведомлений"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    # ----- Доп. действия -----

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        Notification.objects.filter(user=request.user, is_seen=False).update(is_seen=True)
        return Response({'status': 'all notifications marked as read'})

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_seen = True
        notification.save()
        return Response({'status': 'notification marked as read'})
