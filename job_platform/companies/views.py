from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from django.db.models import Count, Q
from rest_framework.viewsets import ReadOnlyModelViewSet
from companies.models import Company
from companies.serializers import CompanySerializer, CompanyDetailSerializer
from users.models import Employer
from .models import CompanyJoinRequest
from .serializers import CompanyJoinRequestSerializer
from .models import Vacancy, Application
from .serializers import VacancySerializer
from users.permissions import IsOwnerOrReadOnly
from .serializers import ApplicationSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework import filters

from companies.ai_services import find_best_resumes_for_vacancy
from resumes.models import Resume

class CompanyJoinRequestViewSet(viewsets.ModelViewSet):
    queryset = CompanyJoinRequest.objects.all()
    serializer_class = CompanyJoinRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return CompanyJoinRequest.objects.filter(company__owner=user)

    @action(detail=True, methods=['post'], url_path='approve')
    def approve_request(self, request, pk=None):
        join_request = self.get_object()
        if join_request.company.owner != request.user:
            return Response({"detail": "Вы не владелец этой компании"},
                            status=status.HTTP_403_FORBIDDEN)
        join_request.status = 'approved'
        join_request.save()
        user = join_request.user
        user.company = join_request.company
        user.save()

        Employer.objects.create(user=user, company=join_request.company)

        return Response({"detail": "Запрос одобрен!"})

    @action(detail=True, methods=['post'], url_path='reject')
    def reject_request(self, request, pk=None):
        join_request = self.get_object()
        if join_request.company.owner != request.user:
            return Response({"detail": "Вы не владелец этой компании"},
                            status=status.HTTP_403_FORBIDDEN)

        join_request.status = 'rejected'
        join_request.save()
        return Response({"detail": "Запрос отклонён!"})

class VacancyViewSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'category', 'city', 'employment_type', 'experience',
        'currency', 'is_active', 'company'
    ]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'salary_from', 'salary_to']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.request.method in ['GET'] and (
            self.request.query_params.get('public') == 'true' or 
            self.action == 'retrieve' or 
            self.action == 'list'
        ):
            return [permissions.AllowAny()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        user = self.request.user
        if not user.company:
            raise PermissionDenied("Вы не связаны с компанией")

        serializer.save(
            company=user.company,
            created_by=user
        )
        
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if instance.company:
            instance.company.active_vacancies_count = Vacancy.objects.filter(
                company=instance.company, 
                is_active=True
            ).count()
            
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="top-resumes")
    def top_resumes(self, request, pk=None):
        vacancy = self.get_object()
        resumes = Resume.objects.all()[:10] 
        result = find_best_resumes_for_vacancy(vacancy, resumes)
        return Response({"top_matches": result})

class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]  

    def perform_create(self, serializer):
        user = self.request.user

        if user.role != 'job_seeker':
            raise PermissionDenied("Только соискатель может откликаться")

        if not hasattr(user, 'job_seeker_profile'):
            raise PermissionDenied("У вас нет job_seeker_profile")

        job_seeker = user.job_seeker_profile  

        try:
            serializer.save(job_seeker=job_seeker, status='pending')
        except IntegrityError:
            raise ValidationError({"detail": "Вы уже откликались на эту вакансию"})

    def update(self, request, *args, **kwargs):
        application = self.get_object()
        user = request.user
        if user.role != 'employer':
            raise PermissionDenied("Только работодатель может обновлять статус отклика")

        if not user.company:
            raise PermissionDenied("У вас нет компании")

        if application.vacancy.company != user.company:
            raise PermissionDenied("Вы не владелец этой вакансии")

        return super().update(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()

        if user.role == 'job_seeker':
            return qs.filter(job_seeker=user.job_seeker_profile)
        elif user.role == 'employer':
            return qs.filter(vacancy__company=user.company)
        else:
            return qs.none()

class CompanyViewSet(ReadOnlyModelViewSet):
    """
    GET /api/companies/          — список компаний
    GET /api/companies/{id}/     — детали компании
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = CompanySerializer

    def get_queryset(self):
        return (
            Company.objects.all()
            .annotate(
                active_vacancies_count=Count(
                    "vacancies", filter=Q(vacancies__is_active=True)
                )
            )
            .select_related("owner")
        )
    

from .models import JobCategory
from .serializers import JobCategorySerializer

class JobCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/companies/categories/ - список всех категорий вакансий
    GET /api/companies/categories/{id}/ - детали категории
    GET /api/companies/categories/{id}/vacancies/ - вакансии в категории
    """
    queryset = JobCategory.objects.all()
    serializer_class = JobCategorySerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return (
            JobCategory.objects.all()
            .annotate(
                vacancies_count=Count(
                    "vacancies", filter=Q(vacancies__is_active=True)
                )
            )
        )
        
    @action(detail=True, methods=["get"], url_path="vacancies")
    def get_category_vacancies(self, request, pk=None):
        """Получить вакансии определенной категории"""
        category = self.get_object()
        vacancies = Vacancy.objects.filter(category=category, is_active=True)
        
        # Поддержка пагинации
        page = self.paginate_queryset(vacancies)
        if page is not None:
            serializer = VacancySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = VacancySerializer(vacancies, many=True)
        return Response(serializer.data)