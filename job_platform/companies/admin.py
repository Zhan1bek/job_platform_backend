from django.contrib import admin
from .models import Vacancy, JobCategory, Company, CompanyJoinRequest, Application
from .models import FavoriteVacancy
admin.site.register(Vacancy)
admin.site.register(JobCategory)
admin.site.register(Company)
admin.site.register(CompanyJoinRequest)
admin.site.register(Application)

admin.site.register(FavoriteVacancy)
