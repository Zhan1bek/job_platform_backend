from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError

from users.models import Employer
from .models import CompanyJoinRequest
from .serializers import CompanyJoinRequestSerializer
from .models import Vacancy, Application
from .serializers import VacancySerializer
from users.permissions import IsOwnerOrReadOnly

from rest_framework.exceptions import PermissionDenied
from .serializers import ApplicationSerializer
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import FavoriteVacancy
from .serializers import FavoriteVacancySerializer

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

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'location', 'is_active', 'company']

    def perform_create(self, serializer):
        """
        При создании вакансии нужно убедиться, что текущий пользователь (request.user)
        является сотрудником какой-то компании.
        Заполним fields: company=..., created_by=...
        """
        user = self.request.user
        if not user.company:
            return Response(
                {"detail": "У вас нет компании, вы не можете создавать вакансии."},
                status=status.HTTP_403_FORBIDDEN
            )
        # Если нужно проверять конкретную роль:
        # if user.role != 'employer':
        #     return Response(...)

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

class FavoriteVacancyViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteVacancySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FavoriteVacancy.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != 'job_seeker':
            raise PermissionDenied("Только соискатели могут добавлять в избранное.")
        serializer.save(user=user)