from io import BytesIO
from django.core.files.base import ContentFile
from django.db import models
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from users.models import JobSeeker


class Resume(models.Model):
    job_seeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE, related_name='resumes')

    # 🔹 Основная информация
    full_name = models.CharField(max_length=255, null=True)
    email = models.EmailField(null=True)
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)

    # 🔹 Ссылки
    linkedin_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    portfolio_url = models.URLField(blank=True, null=True)

    # 🔹 Контент
    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True)
    skills = models.TextField(blank=True, help_text="Через запятую")
    education = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    certifications = models.TextField(blank=True)
    languages = models.CharField(max_length=255, blank=True)
    interests = models.TextField(blank=True)
    additional_info = models.TextField(blank=True)

    # 🔹 PDF-файл
    pdf_file = models.FileField(upload_to="resumes/%Y/%m/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def build_pdf(self):
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        x = 50
        y = 800

        def write(label, value, step=25):
            nonlocal y
            p.setFont("Helvetica-Bold", 11)
            p.drawString(x, y, label)
            p.setFont("Helvetica", 11)
            p.drawString(x + 150, y, value or "-")
            y -= step

        p.setFont("Helvetica-Bold", 16)
        p.drawString(x, y, f"{self.full_name} — {self.title}")
        y -= 40

        write("Email:", self.email)
        write("Phone:", self.phone_number)
        write("Address:", self.address)
        write("LinkedIn:", self.linkedin_url)
        write("GitHub:", self.github_url)
        write("Portfolio:", self.portfolio_url)
        write("Summary:", self.summary)
        write("Skills:", self.skills)
        write("Education:", self.education)
        write("Experience:", self.experience)
        write("Certifications:", self.certifications)
        write("Languages:", self.languages)
        write("Interests:", self.interests)
        write("Additional Info:", self.additional_info)

        p.showPage()
        p.save()
        pdf = buffer.getvalue()
        buffer.close()

        self.pdf_file.save(f"resume_{self.pk}.pdf", ContentFile(pdf), save=True)

    def __str__(self):
        return f"{self.full_name} ({self.job_seeker.user.username})"

    class Meta:
        ordering = ("-updated_at",)
        unique_together = ("job_seeker", "title")
