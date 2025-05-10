import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        from django.contrib.auth import get_user_model
        from .models import Message
        User = get_user_model()

        data = json.loads(text_data)
        message = data.get('message')
        sender_id = data.get('sender_id')
        recipient_id = data.get('recipient_id')

        sender = await database_sync_to_async(User.objects.get)(id=sender_id)
        recipient = await database_sync_to_async(User.objects.get)(id=recipient_id)

        await database_sync_to_async(Message.objects.create)(
            sender=sender,
            recipient=recipient,
            content=message
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': sender_id,
                'recipient_id': recipient_id,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'recipient_id': event['recipient_id'],
        }))
