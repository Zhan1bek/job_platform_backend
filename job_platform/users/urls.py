from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    JobSeekerRegisterView, 
    EmployerRegisterView, 
    JobSeekerProfileView, 
    ResumeViewSet
)

router = DefaultRouter()
router.register(r'resumes', ResumeViewSet, basename='resumes')

urlpatterns = [
    path('register/jobseeker/', JobSeekerRegisterView.as_view(), name='jobseeker-register'),
    path('register/employer/', EmployerRegisterView.as_view(), name='employer-register'),

    path('jobseeker/profile/', JobSeekerProfileView.as_view(), name='jobseeker-profile'),

    # router на резюме
    path('', include(router.urls)),
]
