from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import JobSeeker, Employer  # и Employer, если нужно

from rest_framework import serializers
from .models import Resume

User = get_user_model()

class JobSeekerRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'phone', 'photo')

    def create(self, validated_data):
        # 1) Создаём пользователя
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        JobSeeker.objects.create(user=user)
        return user


class EmployerRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'phone', 'photo')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        Employer.objects.create(user=user)
        return user


class ResumeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Resume
        fields = '__all__'
        read_only_fields = ('job_seeker', 'created_at', 'updated_at')