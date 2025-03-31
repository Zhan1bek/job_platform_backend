from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.conf import settings


class User(AbstractUser):
    photo = models.ImageField(upload_to='user_photos/', null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    LANGUAGE_CHOICES = (
        ('KAZAKH', 'Kazakh'),
        ('ENGLISH', 'English'),
        ('RUSSIAN', 'Russian'),
    )
    interface_language = models.CharField(
        max_length=10, choices=LANGUAGE_CHOICES, default='ENGLISH'
    )

    def __str__(self):
        return f"{self.username} ({self.first_name} {self.last_name})"


class JobSeeker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='job_seeker_profile')

    languages = models.CharField(max_length=255, blank=True, help_text="Перечислите языки через запятую.")

    def __str__(self):
        return f"JobSeeker: {self.user.username}"


class Employer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employer_profile')

    company = models.ForeignKey('jobs.Company', on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='employers')

    def __str__(self):
        return f"Employer: {self.user.username}"


class Resume(models.Model):
    job_seeker = models.ForeignKey(
        'users.JobSeeker',
        on_delete=models.CASCADE,
        related_name='resumes'
    )
    title = models.CharField(max_length=200, help_text="Название резюме, например 'Backend Developer'.")
    summary = models.TextField(blank=True, help_text="Краткое описание или summary.")
    file = models.FileField(upload_to='resumes/', null=True, blank=True, help_text="PDF")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} (JobSeeker: {self.job_seeker.user.username})"