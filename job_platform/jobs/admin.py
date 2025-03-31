from django.contrib import admin
from .models import Company, Vacancy,  Review

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name',)

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'company', 'work_type', 'work_format', 'work_graph', 'required_experience', 'is_active')
    list_filter = ('work_type', 'work_format', 'work_graph', 'required_experience', 'is_active', 'company')
    search_fields = ('title', 'company__name', 'tags')

# @admin.register(Resume)
# class ResumeAdmin(admin.ModelAdmin):
#     list_display = ('id', 'job_seeker', 'title', 'is_public', 'preferred_work_type')
#     search_fields = ('job_seeker__user__username', 'title', 'skills')
#
# @admin.register(Education)
# class EducationAdmin(admin.ModelAdmin):
#     list_display = ('id', 'resume', 'institution', 'degree', 'start_date', 'end_date', 'gpa')
#     search_fields = ('institution', 'resume__job_seeker__user__username')
#
# @admin.register(Experience)
# class ExperienceAdmin(admin.ModelAdmin):
#     list_display = ('id', 'resume', 'position', 'start_date', 'end_date')
#     search_fields = ('position', 'resume__job_seeker__user__username')
#
# @admin.register(Request)
# class RequestAdmin(admin.ModelAdmin):
#     list_display = ('id', 'job_seeker', 'vacancy', 'resume', 'status', 'created_at')
#     list_filter = ('status',)
#     search_fields = ('job_seeker__user__username', 'vacancy__title')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'job_seeker', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('company__name', 'job_seeker__user__username')
