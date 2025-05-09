from rest_framework import serializers
from resumes.models import Resume
from users.models import JobSeeker
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError


class ResumeSerializer(serializers.ModelSerializer):
    pdf_file = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Resume
        exclude = ("job_seeker",)

    def create(self, validated_data):
        user = self.context["request"].user
        if getattr(user, "role", None) != "job_seeker":
            raise ValidationError("Только соискатель может создавать резюме")

        job_seeker, _ = JobSeeker.objects.get_or_create(user=user)

        try:
            return Resume.objects.create(job_seeker=job_seeker, **validated_data)
        except IntegrityError:
            raise ValidationError({"title": "У вас уже есть резюме с таким заголовком."})

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance
