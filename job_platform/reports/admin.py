from django.contrib import admin
from .models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'reporter', 'target_type', 'target_id', 'is_resolved', 'created_at')
    list_filter = ('target_type', 'is_resolved', 'created_at')
    search_fields = ('reason', 'reporter__username')
    ordering = ('-created_at',)
