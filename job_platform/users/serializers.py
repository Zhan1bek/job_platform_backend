from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import JobSeeker, Employer

from .models import Resume
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()
from django.contrib.auth import get_user_model
from companies.models import Company, CompanyJoinRequest



User = get_user_model()

class EmployerRegistrationSerializer(serializers.ModelSerializer):
    # Дополнительные поля, которые приходят при регистрации
    join_type = serializers.ChoiceField(choices=['create','join'], write_only=True)
    company_name = serializers.CharField(max_length=255, required=False)
    company_id = serializers.IntegerField(required=False)

    class Meta:
        model = User
        fields = (
            'username', 'password', 'email',
            'join_type', 'company_name', 'company_id'
        )

    def create(self, validated_data):
        join_type = validated_data.pop('join_type', None)
        company_name = validated_data.pop('company_name', None)
        company_id = validated_data.pop('company_id', None)

        # Создаём самого пользователя (employer)
        user = User(
            username=validated_data['username'],
            email=validated_data.get('email'),
            role='employer'
        )
        user.set_password(validated_data['password'])
        user.save()

        if join_type == 'create':
            # 1) Создать компанию
            if not company_name:
                raise serializers.ValidationError("company_name is required for creating a new company")
            new_company = Company.objects.create(name=company_name, owner=user)
            # Привязываем user к компании
            user.company = new_company
            user.save()

            # И сразу создаём Employer-объект
            employer = Employer.objects.create(user=user, company=new_company)

        elif join_type == 'join':
            # 2) Запрос на вступление в уже существующую компанию
            if not company_id:
                raise serializers.ValidationError("company_id is required to join existing company")
            try:
                existing_company = Company.objects.get(id=company_id)
            except Company.DoesNotExist:
                raise serializers.ValidationError("Company does not exist")

            # Создаём заявку (pending)
            CompanyJoinRequest.objects.create(
                user=user,
                company=existing_company,
                status='pending'
            )
            # company у user пока не заполняем!
            # Ждём одобрения владельцем

        return user


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