from django.db import models
from users.models import User
from users.models import JobSeeker, Employer

class Chat(models.Model):
    job_seeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE, related_name='chats')
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE, related_name='chats')

    def __str__(self):
        return f"Chat between {self.job_seeker.user.username} and {self.employer.user.username}"


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    attachment = models.FileField(upload_to='chat_attachments/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} at {self.timestamp}"
