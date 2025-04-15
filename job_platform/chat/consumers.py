import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from .models import Chat, Message

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 1) Определяем ID чата из URL
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f"chat_{self.chat_id}"

        # 2) Проверяем, что user аутентифицирован
        user = self.scope['user']
        if user.is_anonymous:
            # Отклоняем подключение (неавторизован)
            await self.close()
        else:
            # Проверим, действительно ли user участвует в чате
            chat = await self.get_chat(self.chat_id)
            if not chat:
                await self.close()
            else:
                # Можно проверить, состоит ли user в chat.participants
                if not await self.user_in_chat(user, chat):
                    await self.close()
                else:
                    # Присоединяемся к группе
                    await self.channel_layer.group_add(
                        self.room_group_name,
                        self.channel_name
                    )
                    await self.accept()

    async def disconnect(self, close_code):
        # Покидаем группу
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Принимаем сообщение в формате JSON:
        {"message": "Text here"}
        """
        data = json.loads(text_data)
        message_text = data.get("message", "")
        user = self.scope['user']

        # Сохраним сообщение в БД
        chat = await self.get_chat(self.chat_id)
        msg_obj = await self.create_message(chat, user, message_text)

        # Отправим всем участникам
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message_text,
                "sender_id": user.id,
                "sender_username": user.username,
            }
        )

    async def chat_message(self, event):
        """
        Получаем событие chat_message от group_send
        и рассылаем по WebSocket всем участникам
        """
        message_text = event["message"]
        sender_id = event["sender_id"]
        sender_username = event["sender_username"]

        await self.send(text_data=json.dumps({
            "sender_id": sender_id,
            "sender_username": sender_username,
            "message": message_text,
        }))

    @staticmethod
    async def get_chat(chat_id):
        try:
            return Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            return None

    @staticmethod
    async def user_in_chat(user, chat):
        return user in chat.participants.all()

    @staticmethod
    async def create_message(chat, user, text):
        return Message.objects.create(chat=chat, sender=user, text=text)
