from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count, OuterRef, Subquery, Max
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import Conversation, Message, Notification
from .serializers import ConversationSerializer, MessageSerializer, NotificationSerializer
from .permissions import IsConversationParticipant
from users.serializers import UserSerializer

User = get_user_model()

class ConversationViewSet(viewsets.ModelViewSet):
    """API для управления беседами"""
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Возвращает беседы, в которых участвует текущий пользователь"""
        return Conversation.objects.filter(participants=self.request.user)
    
    def get_permissions(self):
        """Определяет права доступа в зависимости от действия"""
        if self.action in ['retrieve', 'messages', 'mark_as_read']:
            return [permissions.IsAuthenticated(), IsConversationParticipant()]
        return super().get_permissions()
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Получить все сообщения в беседе"""
        conversation = self.get_object()
        page = self.paginate_queryset(conversation.messages.all())
        
        if page is not None:
            serializer = MessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = MessageSerializer(conversation.messages.all(), many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Отправить сообщение в беседу"""
        conversation = self.get_object()
        serializer = MessageSerializer(data={
            'conversation': conversation.id,
            'sender': request.user.id,
            'content': request.data.get('content')
        })
        
        if serializer.is_valid():
            message = serializer.save()
            
            # Создаем уведомления для других участников
            for participant in conversation.participants.exclude(id=request.user.id):
                Notification.objects.create(
                    user=participant,
                    conversation=conversation,
                    message=message
                )
            
            # Обновляем timestamp беседы
            conversation.save()  # auto_now=True обновит updated_at
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Отметить все сообщения в беседе как прочитанные"""
        conversation = self.get_object()
        messages = conversation.messages.filter(is_read=False).exclude(sender=request.user)
        
        # Отмечаем сообщения как прочитанные
        messages.update(is_read=True)
        
        # Отмечаем уведомления как прочитанные
        Notification.objects.filter(
            user=request.user,
            conversation=conversation,
            is_read=False
        ).update(is_read=True)
        
        return Response({'status': 'messages marked as read'})
    
    @action(detail=False, methods=['get'])
    def create_or_get_direct(self, request):
        """Создать или получить прямую беседу с другим пользователем"""
        user_id = request.query_params.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            other_user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        conversation, created = Conversation.get_or_create_conversation(
            request.user, other_user
        )
        
        serializer = ConversationSerializer(
            conversation, 
            context={'request': request}
        )
        
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    """API для управления сообщениями"""
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsConversationParticipant]
    
    def get_queryset(self):
        """Возвращает сообщения из бесед, в которых участвует пользователь"""
        user_conversations = Conversation.objects.filter(participants=self.request.user)
        return Message.objects.filter(conversation__in=user_conversations)
    
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """API для уведомлений о сообщениях"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Возвращает уведомления для текущего пользователя"""
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Отметить все уведомления как прочитанные"""
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'status': 'all notifications marked as read'})
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Отметить конкретное уведомление как прочитанное"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'notification marked as read'})