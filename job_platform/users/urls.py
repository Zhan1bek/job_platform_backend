from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from .views import (
    JobSeekerRegisterView, EmployerRegisterView,
    JobSeekerProfileView, EmployerProfileView,
    ChangePasswordView,
    universal_register, jobseeker_dashboard, employer_dashboard_view, employer_profile_view  # ← только его оставляем
)
from .views import main_page
from .views import dashboard_view
from .views import CustomLoginView, dashboard_view


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
    path('login/', CustomLoginView.as_view(), name='login'),
    path('dashboard/jobseeker/', jobseeker_dashboard, name='jobseeker-dashboard'),
    path('dashboard/employer/', employer_dashboard_view, name='employer-dashboard'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('dashboard/employer/profile/', employer_profile_view, name='employer-profile'),
]
