from django.db import models
from django.conf import settings
from django.utils import timezone
from users.models import JobSeeker

class Company(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='company_logos/', null=True, blank=True)
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=100, blank=True)
    founded_year = models.IntegerField(null=True, blank=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_companies',
        null=True, blank=True
    )

    def __str__(self):
        return self.name


class CompanyJoinRequest(models.Model):
    """
    Заявка пользователя (employer) на вступление в существующую компанию.
    """
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


class JobCategory(models.Model):
    """
    Категория / сфера работы, например: IT, Marketing, Sales и т.д.
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Vacancy(models.Model):
    EMPLOYMENT_TYPES = [
        ('FULL', 'Full-time'),
        ('PART', 'Part-time'),
        ('CONTRACT', 'Contract'),
    ]

    EXPERIENCE_LEVELS = [
        ('JUNIOR', 'Junior'),
        ('MID', 'Middle'),
        ('SENIOR', 'Senior'),
    ]

    CURRENCIES = [
        ('KZT', 'KZT'),
        ('USD', 'USD'),
        ('EUR', 'EUR'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='vacancies')
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    category = models.ForeignKey('JobCategory', on_delete=models.SET_NULL, null=True, blank=True, related_name='vacancies')

    location = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    salary_from = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_to = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, choices=CURRENCIES, default='KZT')
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPES, default='FULL')
    experience = models.CharField(max_length=10, choices=EXPERIENCE_LEVELS, default='MID')

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} at {self.company.name}"


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
