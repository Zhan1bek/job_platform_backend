from django.db import models
from users.models import JobSeeker


# Модель Компании
class Company(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Можно добавить адрес, сайт и т.д.

    def __str__(self):
        return self.name


# Модель Вакансии
class Vacancy(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='vacancies')
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField(blank=True)

    WORK_TYPE_CHOICES = (
        ('FULL', 'Full-time'),
        ('PARTIAL', 'Part-time'),
        ('PROJECT', 'Project-based'),
        ('VOLUNTEERING', 'Volunteering'),
        ('INTERNSHIP', 'Internship'),
    )
    work_type = models.CharField(max_length=20, choices=WORK_TYPE_CHOICES)

    WORK_FORMAT_CHOICES = (
        ('OFFICE', 'Office'),
        ('REMOTE', 'Remote'),
    )
    work_format = models.CharField(max_length=10, choices=WORK_FORMAT_CHOICES)

    WORK_GRAPH_CHOICES = (
        ('TWOBYTWO', '2x2'),
        ('FIVEBYTWO', '5x2'),
    )
    work_graph = models.CharField(max_length=10, choices=WORK_GRAPH_CHOICES)

    REQUIRED_EXPERIENCE_CHOICES = (
        ('NONE', 'No experience'),
        ('FROM1TO2', '1-2 years'),
        ('FROM2TO4', '2-4 years'),
        ('FROM4TO6', '4-6 years'),
        ('PLUS6', 'More than 6 years'),
    )
    required_experience = models.CharField(max_length=10, choices=REQUIRED_EXPERIENCE_CHOICES)

    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    region = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.title} at {self.company.name}"


# Модель Резюме
class Resume(models.Model):
    job_seeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(max_length=255, blank=True)
    skills = models.TextField(blank=True, help_text="Перечислите навыки через запятую.")

    def __str__(self):
        return f"Resume of {self.job_seeker.user.username}"


# Модель Образования
class Education(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='educations')
    institution = models.CharField(max_length=255)
    DEGREE_CHOICES = (
        ('BACHELOR', 'Bachelor'),
        ('MASTER', 'Master'),
        ('PHD', 'PhD'),
    )
    degree = models.CharField(max_length=10, choices=DEGREE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.degree} at {self.institution}"


# Модель Опыт работы
class Experience(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='experiences')
    position = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.position} ({self.resume.job_seeker.user.username})"


# Модель Запроса на работу
class Request(models.Model):
    job_seeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE, related_name='job_requests')
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='requests')
    resume = models.ForeignKey(Resume, on_delete=models.SET_NULL, null=True, blank=True)

    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('DECLINED', 'Declined'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request by {self.job_seeker.user.username} for {self.vacancy.title}"


# Модель Отзыва
class Review(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='reviews')
    job_seeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(help_text="Оценка от 1 до 5")
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.job_seeker.user.username} for {self.company.name}"
