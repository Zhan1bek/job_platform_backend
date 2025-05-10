from .models import CompanyJoinRequest, Vacancy, Application, Company, JobCategory
from django.contrib.auth import get_user_model
from rest_framework import serializers

class CompanyJoinRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyJoinRequest
        fields = ['id', 'user', 'company', 'status', 'created_at']
        read_only_fields = ['status', 'created_at']

class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "first_name", "last_name", "email")

class CompanyDetailSerializer(serializers.ModelSerializer):
    """Расширенный сериализатор для детальной информации о компании"""
    owner = OwnerSerializer(read_only=True)
    active_vacancies_count = serializers.IntegerField(read_only=True, default=0)
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'description', 'industry', 'website', 
            'logo', 'founded_year', 'owner', 'active_vacancies_count'
        ]

class CompanySerializer(serializers.ModelSerializer):
    owner = OwnerSerializer(read_only=True)
    active_vacancies_count = serializers.IntegerField(read_only=True, default=0)
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'description', 'industry', 'website', 
            'logo', 'founded_year', 'owner', 'active_vacancies_count'
        ]

class VacancySerializer(serializers.ModelSerializer):
    # Добавляем детальную информацию о компании
    company = CompanyDetailSerializer(read_only=True)
    # Поле для создания/обновления вакансии (только ID)
    company_id = serializers.PrimaryKeyRelatedField(
        source='company', 
        queryset=Company.objects.all(), 
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Vacancy
        fields = '__all__'
        read_only_fields = ['company', 'created_by', 'created_at', 'updated_at']

class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = [
            'id',
            'vacancy',
            'job_seeker',
            'status',
            'cover_letter',
            'created_at'
        ]
        read_only_fields = ['id', 'job_seeker', 'created_at']

class JobCategorySerializer(serializers.ModelSerializer):
    vacancies_count = serializers.IntegerField(read_only=True, default=0)
    
    class Meta:
        model = JobCategory
        fields = ['id', 'name', 'vacancies_count']