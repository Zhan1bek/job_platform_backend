from django.db import models
from django.conf import settings
from django.utils import timezone

REPORT_TARGET_CHOICES = [
    ('vacancy', 'Vacancy'),
    ('comment', 'Comment'),
    ('publication', 'Publication'),
    ('message', 'Message'),
    ('user', 'User'),
]

class Report(models.Model):
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports_made')
    target_type = models.CharField(max_length=20, choices=REPORT_TARGET_CHOICES)
    target_id = models.PositiveIntegerField()
    reason = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.reporter.username} reported {self.target_type}#{self.target_id}"
