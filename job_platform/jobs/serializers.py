from rest_framework import serializers
from companies.models import Vacancy

class VacancySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacancy
        fields = '__all__'

# class ResumeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Resume
#         fields = '__all__'
#
# class RequestSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Request
#         fields = '__all__'
#
# class ReviewSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Review
#         fields = '__all__'
