from django.urls import path
from .views import JobSeekerRegisterView, EmployerRegisterView
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ResumeViewSet

router = DefaultRouter()
router.register(r'resumes', ResumeViewSet, basename='resumes')

urlpatterns = [
    path('register/jobseeker/', JobSeekerRegisterView.as_view(), name='jobseeker-register'),
    path('register/employer/', EmployerRegisterView.as_view(), name='employer-register'),
    path('', include(router.urls)),
]