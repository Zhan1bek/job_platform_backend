from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CompanyJoinRequestViewSet,
    # CompanyViewSet,
    VacancyViewSet
)

router = DefaultRouter()
router.register(r'join-requests', CompanyJoinRequestViewSet, basename='company-join-requests')
router.register(r'vacancies', VacancyViewSet, basename='vacancies')  # CRUD для вакансий


# router.register(r'companies', CompanyViewSet, basename='companies')

urlpatterns = [
    path('', include(router.urls)),
]
