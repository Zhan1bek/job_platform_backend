from rest_framework import viewsets, permissions
from .models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer
from rest_framework.exceptions import PermissionDenied

class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'job_seeker' and hasattr(user, 'job_seeker_profile'):
            return Chat.objects.filter(job_seeker=user.job_seeker_profile)
        elif user.role == 'employer' and hasattr(user, 'employer_profile'):
            return Chat.objects.filter(employer=user.employer_profile)
        return Chat.objects.none()


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Message.objects.all()

        # фильтровать по chat
        chat_id = self.request.query_params.get('chat')
        if chat_id:
            qs = qs.filter(chat_id=chat_id)

        # ограничить только участникам чата
        if user.role == 'job_seeker' and hasattr(user, 'job_seeker_profile'):
            qs = qs.filter(chat__job_seeker=user.job_seeker_profile)
        elif user.role == 'employer' and hasattr(user, 'employer_profile'):
            qs = qs.filter(chat__employer=user.employer_profile)
        else:
            qs = qs.none()

        return qs

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)