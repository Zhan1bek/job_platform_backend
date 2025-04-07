from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from users.models import Employer
from .models import CompanyJoinRequest
from .serializers import CompanyJoinRequestSerializer
from .models import Vacancy
from .serializers import VacancySerializer
from users.permissions import IsOwnerOrReadOnly


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
