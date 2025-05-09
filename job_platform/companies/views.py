from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from django.db.models import Count, Q
from rest_framework.viewsets import ReadOnlyModelViewSet
from companies.models import Company
from companies.serializers import CompanySerializer
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
from rest_framework.decorators import action







class CompanyJoinRequestViewSet(viewsets.ModelViewSet):
    queryset = CompanyJoinRequest.objects.all()
    serializer_class = CompanyJoinRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Например, владелец видит заявки в своих компаниях.
        Либо если нужен супердоступ - меняем логику.
        """
        user = self.request.user
        # Возвращать заявки, где company.owner == user
        return CompanyJoinRequest.objects.filter(company__owner=user)

    @action(detail=True, methods=['post'], url_path='approve')
    def approve_request(self, request, pk=None):
        join_request = self.get_object()
        # Проверяем, что current_user == owner
        if join_request.company.owner != request.user:
            return Response({"detail": "Вы не владелец этой компании"},
                            status=status.HTTP_403_FORBIDDEN)
        # Ставим статус approved
        join_request.status = 'approved'
        join_request.save()
        # Записываем user.company = join_request.company
        user = join_request.user
        user.company = join_request.company
        user.save()

        # Создаём Employer
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

    def perform_create(self, serializer):
        user = self.request.user
        if not user.company:
            raise PermissionDenied("Вы не связаны с компанией")

        serializer.save(
            company=user.company,
            created_by=user
        )



class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]  # + custom permissions

    def perform_create(self, serializer):
        user = self.request.user

        # 1) Проверяем, что user - job_seeker
        if user.role != 'job_seeker':
            raise PermissionDenied("Только соискатель может откликаться")

        if not hasattr(user, 'job_seeker_profile'):
            raise PermissionDenied("У вас нет job_seeker_profile")

        job_seeker = user.job_seeker_profile  # OneToOne

        try:
            serializer.save(job_seeker=job_seeker, status='pending')
        except IntegrityError:
            raise ValidationError({"detail": "Вы уже откликались на эту вакансию"})

        # 2) Сохраняем с default status='pending'
        # serializer.validated_data['vacancy'] - тот vacancy_id, что пришёл с POST
        serializer.save(job_seeker=job_seeker, status='pending')

    def update(self, request, *args, **kwargs):
        """
        Переопределим update для изменения `status`.
        Проверяем, что user = employer компании, где эта вакансия.
        """
        application = self.get_object()
        user = request.user

        # Проверяем, что user - employer и принадлежит той же компании:
        # vacancy -> company == user.company
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
            # показываем только отклики, где job_seeker = user.job_seeker_profile
            return qs.filter(job_seeker=user.job_seeker_profile)
        elif user.role == 'employer':
            # показываем только отклики на вакансии его компании
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


@action(detail=True, methods=["get"], url_path="top-resumes")
def top_resumes(self, request, pk=None):
    vacancy = self.get_object()
    resumes = Resume.objects.all()[:10]  # пока что до 10, можно фильтровать
    result = find_best_resumes_for_vacancy(vacancy, resumes)
    return Response({"top_matches": result})