from django.contrib import admin
from .models import Vacancy, JobCategory, Company, CompanyJoinRequest, Application
admin.site.register(Vacancy)
admin.site.register(JobCategory)
admin.site.register(Company)
admin.site.register(CompanyJoinRequest)
admin.site.register(Application)

