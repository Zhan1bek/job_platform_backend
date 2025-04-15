# chat/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone


class Chat(models.Model):
    """
    Модель чата (комнаты).
    participants = ManyToManyField к User
    """
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='chats'
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Chat {self.id}"

class Message(models.Model):
    """
    Сообщение в чате.
    """
    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Msg {self.id} from {self.sender.username} in chat {self.chat.id}"

