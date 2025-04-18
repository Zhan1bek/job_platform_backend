from rest_framework import generics
from .serializers import JobSeekerRegistrationSerializer, EmployerRegistrationSerializer

from rest_framework import viewsets, permissions, status
from .models import Resume
from .serializers import ResumeSerializer
from .permissions import IsOwnerOrReadOnly

from .models import JobSeeker
from .serializers import JobSeekerSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer


from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model


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




class JobSeekerProfileView(generics.RetrieveUpdateAPIView):
    queryset = JobSeeker.objects.all()
    serializer_class = JobSeekerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Возвращаем профиль текущего пользователя (job_seeker_profile)
        # Предполагаем, что user -> job_seeker_profile (OneToOne)
        # Если нет job_seeker_profile, выкидываем 404 или создаём его
        return self.request.user.job_seeker_profile




class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer




User = get_user_model()

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user

        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        new_password_confirm = request.data.get('new_password_confirm')

        if not user.check_password(old_password):
            return Response({"detail": "Старый пароль неверный."}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != new_password_confirm:
            return Response({"detail": "Пароли не совпадают."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({"detail": "Пароль успешно изменён."}, status=status.HTTP_200_OK)

