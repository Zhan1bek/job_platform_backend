from rest_framework import serializers
from .models import Report

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'reporter', 'target_type', 'target_id', 'reason', 'is_resolved', 'created_at']
        read_only_fields = ['id', 'reporter', 'is_resolved', 'created_at']
