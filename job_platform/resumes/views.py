from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Exists, OuterRef

from resumes.models import Resume
from resumes.serializers import ResumeSerializer
from resumes.permissions import ResumePermission
from companies.models import Application


def get_jobseeker_profile(user):
    """Универсальный способ получить профиль соискателя."""
    return getattr(user, "job_seeker_profile", None) or getattr(user, "jobseeker", None)


class ResumeViewSet(viewsets.ModelViewSet):
    """
    /api/resumes/

    Поддержка:
    - GET (list, retrieve)
    - POST (create)
    - PATCH (update)
    - DELETE (destroy)
    - POST /{id}/export-pdf/ — генерация PDF
    """

    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated, ResumePermission]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Resume.objects.all()

        # Соискатель — только свои резюме
        job_seeker = get_jobseeker_profile(user)
        if job_seeker:
            return Resume.objects.filter(job_seeker=job_seeker)

        # Работодатель — только резюме откликнувшихся
        if getattr(user, "company", None):
            apps = Application.objects.filter(
                vacancy__company=user.company,
                job_seeker=OuterRef("job_seeker")
            )
            return Resume.objects.filter(Exists(apps))

        return Resume.objects.none()

    @action(detail=True, methods=["post"], url_path="export-pdf")
    def export_pdf(self, request, pk=None):
        """
        Генерация PDF-файла резюме.
        Если уже есть — возвращает ссылку.
        Если передан { "force": "true" } — пересоздаёт.
        """
        resume = self.get_object()
        force = request.data.get("force") == "true"

        if resume.pdf_file and not force:
            return Response(
                {"pdf_url": request.build_absolute_uri(resume.pdf_file.url)},
                status=status.HTTP_200_OK
            )

        resume.build_pdf()
        return Response(
            {"pdf_url": request.build_absolute_uri(resume.pdf_file.url)},
            status=status.HTTP_201_CREATED
        )
