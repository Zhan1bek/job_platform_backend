from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CompanyJoinRequestViewSet,
    VacancyViewSet,
    ApplicationViewSet,
    CompanyViewSet,
    JobCategoryViewSet
)

router = DefaultRouter()
router.register(r'join-requests', CompanyJoinRequestViewSet, basename='company-join-requests')
router.register(r'vacancies', VacancyViewSet, basename='vacancies')  # CRUD для вакансий
router.register(r'applications', ApplicationViewSet, basename='application')
router.register(r"companies", CompanyViewSet, basename="company")
router.register(r'categories', JobCategoryViewSet, basename='job-category') 

urlpatterns = [
    path('', include(router.urls)),
]
