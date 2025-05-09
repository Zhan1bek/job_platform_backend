from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    JobSeekerRegisterView,
    EmployerRegisterView,
    JobSeekerProfileView,
    ChangePasswordView, EmployerProfileView
)

router = DefaultRouter()

urlpatterns = [
    path('register/jobseeker/', JobSeekerRegisterView.as_view(), name='jobseeker-register'),
    path('register/employer/', EmployerRegisterView.as_view(), name='employer-register'),
    path('change_password/', ChangePasswordView.as_view(), name='change_password'),

    path('jobseeker/profile/', JobSeekerProfileView.as_view(), name='jobseeker-profile'),
    path("employers/profile/", EmployerProfileView.as_view(), name="employer-profile"),

    path('', include(router.urls)),
]
