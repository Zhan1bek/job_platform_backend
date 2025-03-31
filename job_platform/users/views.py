from rest_framework import generics
from .serializers import JobSeekerRegistrationSerializer, EmployerRegistrationSerializer

from rest_framework import viewsets, permissions
from .models import Resume
from .serializers import ResumeSerializer
from .permissions import IsOwnerOrReadOnly




class JobSeekerRegisterView(generics.CreateAPIView):
    serializer_class = JobSeekerRegistrationSerializer

class EmployerRegisterView(generics.CreateAPIView):
    serializer_class = EmployerRegistrationSerializer



class ResumeViewSet(viewsets.ModelViewSet):
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer

    # Разберёмся с permissions
    # - нужно проверять, что user аутентифицирован
    # - только владелец может менять
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        """
        При создании резюме автоматически укажем job_seeker = текущий пользователь
        (если он вообще JobSeeker).
        """
        user = self.request.user
        # Предполагаем, что у user есть related_name='job_seeker_profile'
        # (OneToOne: user -> JobSeeker)
        if hasattr(user, 'job_seeker_profile'):
            job_seeker = user.job_seeker_profile
            serializer.save(job_seeker=job_seeker)
        else:
            # Если пользователь не job_seeker, можно выбросить ошибку
            raise ValueError("Вы не являетесь соискателем")
