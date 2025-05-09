from django.contrib import admin
from .models import Vacancy, JobCategory, Company, CompanyJoinRequest, Application
admin.site.register(Vacancy)
admin.site.register(JobCategory)
admin.site.register(CompanyJoinRequest)
admin.site.register(Application)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "industry")
    search_fields = ("name", "industry")