from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FavoriteVacancyViewSet
from .views import (
    CompanyJoinRequestViewSet,
    VacancyViewSet,
    ApplicationViewSet,
    CompanyViewSet
)

router = DefaultRouter()
router.register(r'favorites', FavoriteVacancyViewSet, basename='favorites')
router.register(r'join-requests', CompanyJoinRequestViewSet, basename='company-join-requests')
router.register(r'vacancies', VacancyViewSet, basename='vacancies')  # CRUD для вакансий
router.register(r'applications', ApplicationViewSet, basename='application')
router.register(r"companies", CompanyViewSet, basename="company")

urlpatterns = [
    path('', include(router.urls)),
]
