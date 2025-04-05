from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import JobSeeker, Employer  # и Employer, если нужно

from rest_framework import serializers
from .models import Resume
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'photo', 'phone', 'email']

class JobSeekerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = JobSeeker
        fields = ['id', 'languages', 'user']

    def update(self, instance, validated_data):
        # validated_data для JobSeeker, а внутри user-данные
        user_data = validated_data.pop('user', None)
        # Обновляем поля JobSeeker
        instance.languages = validated_data.get('languages', instance.languages)
        instance.save()

        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()

        return instance

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        # Добавим username
        data['username'] = user.username

        # Определим роль
        if hasattr(user, 'job_seeker_profile'):
            data['role'] = 'jobseeker'
        elif hasattr(user, 'employer_profile'):
            data['role'] = 'employer'
        else:
            data['role'] = 'unknown'

        return data