from rest_framework import viewsets, permissions
from .models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer
from rest_framework.exceptions import PermissionDenied

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from .models import Chat
from .serializers import ChatSerializer
from users.models import JobSeeker, Employer

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

    @action(detail=False, methods=['post'], url_path='get-or-create')
    def get_or_create_chat(self, request):
        job_seeker_id = request.data.get("job_seeker_id")
        employer_id = request.data.get("employer_id")

        if not job_seeker_id or not employer_id:
            return Response({"detail": "Нужны job_seeker_id и employer_id"}, status=400)

        try:
            job_seeker = JobSeeker.objects.get(id=job_seeker_id)
            employer = Employer.objects.get(id=employer_id)
        except (JobSeeker.DoesNotExist, Employer.DoesNotExist):
            raise NotFound("Один из профилей не найден")

        chat, created = Chat.objects.get_or_create(
            job_seeker=job_seeker,
            employer=employer
        )

        serializer = self.get_serializer(chat)
        return Response(serializer.data, status=201 if created else 200)



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