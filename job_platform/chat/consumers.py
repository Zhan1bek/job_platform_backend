import json
from django.contrib.auth import get_user_model
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone

from .models import Conversation, Message, Notification

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']

        # Анонимы не подключаются
        if self.user.is_anonymous:
            await self.close()
            return

        # conversation_id из маршрута ws/chat/<uuid>/
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.conversation_group_name = f'chat_{self.conversation_id}'

        # Проверяем, что пользователь — участник беседы
        is_participant = await self.check_user_in_conversation(self.user.id, self.conversation_id)
        if not is_participant:
            await self.close()
            return

        # Подписываемся на группу
        await self.channel_layer.group_add(
            self.conversation_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.conversation_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Принимает два типа сообщений:
        1) {"type": "message", "message": "Hello"}
        2) {"type": "read"}  — отмечает сообщения как прочитанные
        """
        data = json.loads(text_data)
        message_type = data.get('type', 'message')

        if message_type == 'message':
            content = data.get('message')
            message_data = await self.create_message(
                conversation_id=self.conversation_id,
                sender_id=self.user.id,
                content=content
            )

            # Рассылаем новое сообщение всем участникам беседы
            await self.channel_layer.group_send(
                self.conversation_group_name,
                {
                    'type': 'chat_message',
                    'message': message_data
                }
            )

        elif message_type == 'read':
            await self.mark_messages_as_read(
                conversation_id=self.conversation_id,
                user_id=self.user.id
            )

            # Сообщаем участникам, что пользователь прочитал сообщения
            await self.channel_layer.group_send(
                self.conversation_group_name,
                {
                    'type': 'messages_read',
                    'user_id': self.user.id,
                    'conversation_id': self.conversation_id,
                }
            )

    # ↓ Методы‑обработчики входящих событий группы

    async def chat_message(self, event):
        """Отправляет новое сообщение клиенту"""
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message']
        }))

    async def messages_read(self, event):
        """Отправляет уведомление о прочтении"""
        await self.send(text_data=json.dumps({
            'type': 'read_receipt',
            'user_id': event['user_id'],
            'conversation_id': event['conversation_id']
        }))

    # ↓ Синхронные операции с БД через database_sync_to_async

    @database_sync_to_async
    def check_user_in_conversation(self, user_id, conversation_id):
        try:
            conversation = Conversation.objects.get(pk=conversation_id)
            return conversation.participants.filter(id=user_id).exists()
        except Conversation.DoesNotExist:
            return False

    @database_sync_to_async
    def create_message(self, conversation_id, sender_id, content):
        """Создаёт сообщение и уведомления, возвращает данные сообщения"""
        conversation = Conversation.objects.get(pk=conversation_id)
        sender = User.objects.get(pk=sender_id)

        message = Message.objects.create(
            conversation=conversation,
            sender=sender,
            content=content
        )

        # Создаём уведомления для других участников
        for participant in conversation.participants.exclude(id=sender_id):
            Notification.objects.create(
                user=participant,
                conversation=conversation,
                message=message
            )

        # Обновляем time‑stamp беседы
        conversation.updated_at = timezone.now()
        conversation.save()

        return {
            'id': message.id,
            'sender_id': sender.id,
            'sender_name': sender.get_full_name() or sender.username,
            'content': message.content,
            'timestamp': message.timestamp.isoformat(),
            'is_read': message.is_read
        }

    @database_sync_to_async
    def mark_messages_as_read(self, conversation_id, user_id):
        conversation = Conversation.objects.get(pk=conversation_id)

        # Помечаем сообщения как прочитанные
        Message.objects.filter(
            conversation=conversation,
            is_read=False
        ).exclude(sender_id=user_id).update(is_read=True)

        # Помечаем уведомления как просмотренные
        Notification.objects.filter(
            conversation=conversation,
            user_id=user_id,
            is_seen=False
        ).update(is_seen=True)
