from django.db import models
from django.utils import timezone

class Message(models.Model):
    sender = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='sent_messages', null=True, blank=True)
    recipient = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)
    content = models.TextField(default="")
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"From {self.sender} to {self.recipient}"
