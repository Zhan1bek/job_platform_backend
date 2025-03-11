from rest_framework import viewsets
from .models import Vacancy, Resume, Request, Review
from .serializers import VacancySerializer, ResumeSerializer, RequestSerializer, ReviewSerializer
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from .models import Vacancy
from .serializers import VacancySerializer

class VacancyViewSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer

    @swagger_auto_schema(
        operation_description="Получить список вакансий",
        responses={200: VacancySerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Создать новую вакансию",
        request_body=VacancySerializer,
        responses={201: VacancySerializer},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
class ResumeViewSet(viewsets.ModelViewSet):
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer

class RequestViewSet(viewsets.ModelViewSet):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
