from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from .views import (
    JobSeekerRegisterView, EmployerRegisterView,
    JobSeekerProfileView, EmployerProfileView,
    ChangePasswordView,
    universal_register  # ← только его оставляем
)
from .views import main_page
from .views import dashboard_view

router = DefaultRouter()

urlpatterns = [
    # API
    path('api/register/jobseeker/', JobSeekerRegisterView.as_view(), name='jobseeker-register'),
    path('api/register/employer/', EmployerRegisterView.as_view(), name='employer-register'),
    path('api/change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('api/jobseeker/profile/', JobSeekerProfileView.as_view(), name='jobseeker-profile'),
    path('api/employers/profile/', EmployerProfileView.as_view(), name='employer-profile'),
    path('api/', include(router.urls)),

    # HTML

    path('register/', universal_register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
]
