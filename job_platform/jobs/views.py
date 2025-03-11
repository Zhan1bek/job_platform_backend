from rest_framework import viewsets
from .models import Vacancy, Resume, Request, Review
from .serializers import VacancySerializer, ResumeSerializer, RequestSerializer, ReviewSerializer
from django_filters.rest_framework import DjangoFilterBackend

class VacancyViewSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['company', 'work_type', 'region']
class ResumeViewSet(viewsets.ModelViewSet):
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer

class RequestViewSet(viewsets.ModelViewSet):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
