import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Conversation, Message, Notification
from django.utils import timezone

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.conversation_group_name = f'chat_{self.conversation_id}'
        
        is_participant = await self.check_user_in_conversation(self.user.id, self.conversation_id)
        if not is_participant:
            await self.close()
            return
        
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
        data = json.loads(text_data)
        message_type = data.get('type', 'message')
        
        if message_type == 'message':
            content = data.get('message')
            message_data = await self.create_message(
                conversation_id=self.conversation_id,
                sender_id=self.user.id,
                content=content
            )

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
            
            await self.channel_layer.group_send(
                self.conversation_group_name,
                {
                    'type': 'messages_read',
                    'user_id': self.user.id,
                    'conversation_id': self.conversation_id,
                }
            )

    async def chat_message(self, event):
        message_data = event['message']
        
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': message_data
        }))

    async def messages_read(self, event):
        # Отправляем статус прочтения клиенту
        await self.send(text_data=json.dumps({
            'type': 'read_receipt',
            'user_id': event['user_id'],
            'conversation_id': event['conversation_id']
        }))

    @database_sync_to_async
    def check_user_in_conversation(self, user_id, conversation_id):
        """Проверяет, является ли пользователь участником беседы"""
        try:
            conversation = Conversation.objects.get(pk=conversation_id)
            return conversation.participants.filter(id=user_id).exists()
        except Conversation.DoesNotExist:
            return False

    @database_sync_to_async
    def create_message(self, conversation_id, sender_id, content):
        """Создает новое сообщение и возвращает его данные"""
        conversation = Conversation.objects.get(pk=conversation_id)
        sender = User.objects.get(pk=sender_id)
        
        # Создаем сообщение
        message = Message.objects.create(
            conversation=conversation,
            sender=sender,
            content=content
        )
        
        # Создаем уведомления для других участников
        for participant in conversation.participants.exclude(id=sender_id):
            Notification.objects.create(
                user=participant,
                conversation=conversation,
                message=message
            )
        
        # Обновляем время последнего сообщения в беседе
        conversation.updated_at = timezone.now()
        conversation.save()
        
        # Возвращаем данные сообщения
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
        unread_messages = Message.objects.filter(
            conversation=conversation,
            is_read=False
        ).exclude(sender_id=user_id)
        
        unread_messages.update(is_read=True)
        
        Notification.objects.filter(
            conversation=conversation,
            user_id=user_id,
            is_read=False
        ).update(is_read=True)