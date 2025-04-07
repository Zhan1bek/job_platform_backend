from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    photo = models.ImageField(upload_to='user_photos/', null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    ROLES = (
        ('job_seeker', 'Job Seeker'),
        ('employer', 'Employer'),
    )
    role = models.CharField(max_length=20, choices=ROLES, default='job_seeker')

    LANGUAGE_CHOICES = (
        ('KAZAKH', 'Kazakh'),
        ('RUSSIAN', 'Russian'),
        ('ENGLISH', 'English'),
    )
    interface_language = models.CharField(
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default='ENGLISH'
    )

    # Связь с компанией (одна компания — много сотрудников)
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='employees'
    )

    def __str__(self):
        return self.username


class JobSeeker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='job_seeker_profile')
    languages = models.CharField(max_length=255, blank=True, help_text="Перечислите языки через запятую.")

    def __str__(self):
        return f"JobSeeker: {self.user.username}"


class Employer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employer_profile')
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='employers'
    )

    def __str__(self):
        return f"Employer: {self.user.username}"


class Resume(models.Model):
    job_seeker = models.ForeignKey(
        JobSeeker,
        on_delete=models.CASCADE,
        related_name='resumes'
    )
    title = models.CharField(max_length=200, help_text="Название резюме, например 'Backend Developer'.")
    summary = models.TextField(blank=True, help_text="Краткое описание или summary.")
    file = models.FileField(upload_to='resumes/', null=True, blank=True, help_text="PDF файл")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} (JobSeeker: {self.job_seeker.user.username})"
