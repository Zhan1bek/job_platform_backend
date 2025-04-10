from rest_framework import serializers
from .models import CompanyJoinRequest, Vacancy, Application

class CompanyJoinRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyJoinRequest
        fields = ['id', 'user', 'company', 'status', 'created_at']
        read_only_fields = ['status', 'created_at']



class VacancySerializer(serializers.ModelSerializer):
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
