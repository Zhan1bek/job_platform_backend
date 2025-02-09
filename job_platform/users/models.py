from django.contrib.auth.models import AbstractUser
from django.db import models


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
