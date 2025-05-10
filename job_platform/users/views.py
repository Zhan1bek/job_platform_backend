from rest_framework import generics
from .serializers import JobSeekerRegistrationSerializer, EmployerRegistrationSerializer
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from rest_framework.exceptions import PermissionDenied

from users.serializers import EmployerSerializer
from rest_framework import viewsets, permissions, status

from .models import JobSeeker
from .serializers import JobSeekerSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from companies.serializers import CompanySerializer
from rest_framework.exceptions import NotFound

from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import UniversalRegisterForm

from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def dashboard_view(request):
    return render(request, 'users/dashboard.html')


def main_page(request):
    return render(request, 'main.html')

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



class EmployerProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role != "employer":
            raise PermissionDenied("Вы не являетесь сотрудником")

        if not hasattr(user, 'employer_profile'):
            raise NotFound("Профиль сотрудника не найден")

        employer = user.employer_profile
        company = employer.company

        return Response({
            "user_id": user.id,
            "email": user.email,
            "position": employer.position,
            "company": {
                "id": company.id if company else None,
                "name": company.name if company else None,
                "is_owner": company.owner_id == user.id if company else False
            } if company else None
        })

    def patch(self, request):
        user = request.user

        if user.role != "employer":
            raise PermissionDenied("Вы не являетесь сотрудником")

        if not hasattr(user, 'employer_profile'):
            raise NotFound("Профиль сотрудника не найден")

        employer = user.employer_profile
        employer_serializer = EmployerSerializer(employer, data=request.data, partial=True)

        if employer_serializer.is_valid():
            employer_serializer.save()
        else:
            return Response(employer_serializer.errors, status=400)

        # Обновление компании — если юзер является её владельцем
        company_data = request.data.get("company")
        if company_data and employer.company and employer.company.owner_id == user.id:
            company_serializer = CompanySerializer(employer.company, data=company_data, partial=True)
            if company_serializer.is_valid():
                company_serializer.save()
            else:
                return Response(company_serializer.errors, status=400)

        return Response({
            "detail": "Профиль успешно обновлён"
        })


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

def universal_register(request):
    if request.method == 'POST':
        form = UniversalRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.role = form.cleaned_data['role']
            user.save()
            login(request, user)
            if user.role == 'job_seeker':
                return redirect('jobseeker-profile')
            else:
                return redirect('employer-profile')
    else:
        form = UniversalRegisterForm()
    return render(request, 'users/register_universal.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'users/login.html'

    def get_success_url(self):
        user = self.request.user
        if user.role == 'job_seeker':
            return '/api/users/dashboard/jobseeker/'
        elif user.role == 'employer':
            return '/api/users/dashboard/employer/'
        return '/api/users/dashboard/'

@login_required
def jobseeker_dashboard(request):
    return render(request, 'users/jobseeker_dashboard.html')

@login_required
def employer_dashboard_view(request):
    if request.user.role != 'employer':
        return redirect('dashboard')  # обычный дашборд для job_seeker
    return render(request, 'users/employer_dashboard.html')



@login_required
def employer_profile_view(request):
    if request.user.role != 'employer':
        return redirect('dashboard')

    employer = getattr(request.user, 'employer_profile', None)
    company = None
    if employer and employer.company:
        company = {
            'name': employer.company.name,
            'is_owner': employer.company.owner_id == request.user.id
        }

    return render(request, 'users/company_profile.html', {
        'user': request.user,
        'company': company,
    })