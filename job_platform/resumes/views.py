from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Exists, OuterRef

from resumes.models import Resume
from resumes.serializers import ResumeSerializer
from resumes.permissions import ResumePermission
from companies.models import Application, Vacancy

# AI-функции
from resumes.ai_services import evaluate_resume_for_vacancy, recommend_jobs_for_resume, career_advice

def get_jobseeker_profile(user):
    return getattr(user, "job_seeker_profile", None) or getattr(user, "jobseeker", None)

class ResumeViewSet(viewsets.ModelViewSet):
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated, ResumePermission]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Resume.objects.all()

        job_seeker = get_jobseeker_profile(user)
        if job_seeker:
            return Resume.objects.filter(job_seeker=job_seeker)

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

        if resume.pdf_file and force:
            # Удаляем старый PDF
            resume.pdf_file.delete(save=False)

        if not resume.pdf_file or force:
            resume.build_pdf()

        return Response(
            {"pdf_url": request.build_absolute_uri(resume.pdf_file.url)},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"], url_path="evaluate-for/(?P<vacancy_id>[^/.]+)")
    def evaluate_for_vacancy(self, request, pk=None, vacancy_id=None):
        resume = self.get_object()
        try:
            vacancy = Vacancy.objects.get(pk=vacancy_id)
        except Vacancy.DoesNotExist:
            return Response({"error": "Vacancy not found"}, status=status.HTTP_404_NOT_FOUND)

        result = evaluate_resume_for_vacancy(resume, vacancy)
        return Response({"evaluation": result}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="recommend-jobs")
    def recommend_jobs(self, request, pk=None):
        resume = self.get_object()
        vacancies = Vacancy.objects.all()[:20]
        result = recommend_jobs_for_resume(resume, vacancies)
        return Response({"recommendations": result}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="career-advice")
    def career_advice_action(self, request, pk=None):
        resume = self.get_object()
        result = career_advice(resume)
        return Response({"advice": result}, status=status.HTTP_200_OK)
