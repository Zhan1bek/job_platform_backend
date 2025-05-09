from rest_framework import generics
from .serializers import JobSeekerRegistrationSerializer, EmployerRegistrationSerializer

from rest_framework import viewsets, permissions, status
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

