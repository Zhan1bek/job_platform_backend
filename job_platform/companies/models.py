from django.db import models
from django.conf import settings
from django.utils import timezone

class Vacancy(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='vacancies'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} at {self.company.name}"

class Company(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Владелец (owner) компании
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_companies',
        null=True, blank=True
    )

    def __str__(self):
        return self.name


class CompanyJoinRequest(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='company_join_requests'
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='join_requests'
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"JoinRequest: {self.user.username} -> {self.company.name} [{self.status}]"


class Application(models.Model):
    """
    Отклик от соискателя (JobSeeker) на вакансию (Vacancy).
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_review', 'In Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )

    vacancy = models.ForeignKey(
        Vacancy,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    from users.models import JobSeeker
    job_seeker = models.ForeignKey(
        JobSeeker,
        on_delete=models.CASCADE,
        related_name='applications'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    cover_letter = models.TextField(blank=True, help_text="Сопроводительное письмо")
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        unique_together = (('vacancy', 'job_seeker'),)



    def __str__(self):
        return f"Application from {self.job_seeker.user.username} to {self.vacancy.title}"