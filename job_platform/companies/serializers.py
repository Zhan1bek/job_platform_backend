from rest_framework import serializers
from .models import CompanyJoinRequest, Vacancy, Application
from rest_framework import serializers
from .models import FavoriteVacancy

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


class VacancySerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Vacancy
        fields = '__all__'
        read_only_fields = ['company', 'created_by', 'created_at', 'updated_at']

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return FavoriteVacancy.objects.filter(user=user, vacancy=obj).exists()

class FavoriteVacancySerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteVacancy
        fields = ['id', 'user', 'vacancy', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
