from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CompanyJoinRequestViewSet,
    VacancyViewSet,
    ApplicationViewSet,
    CompanyViewSet,
    JobCategoryViewSet, vacancy_create_view, vacancy_list_view, vacancy_detail_view, application_list_view,
    application_accept_view, application_reject_view
)

router = DefaultRouter()
router.register(r'join-requests', CompanyJoinRequestViewSet, basename='company-join-requests')
router.register(r'vacancies', VacancyViewSet, basename='vacancies')  # CRUD для вакансий
router.register(r'applications', ApplicationViewSet, basename='application')
router.register(r"companies", CompanyViewSet, basename="company")
router.register(r'categories', JobCategoryViewSet, basename='job-category') 

urlpatterns = [
    path('', include(router.urls)),

    path('vacancies/create/html/', vacancy_create_view, name='vacancy-create-html'),
    path('vacancies/list/html/', vacancy_list_view, name='vacancy-list-html'),
    path('vacancies/<int:pk>/html/', vacancy_detail_view, name='vacancy-detail'),
    path('applications/list/html/', application_list_view, name='applications-list'),
    path('applications/<int:pk>/accept/', application_accept_view, name='application-accept'),
    path('applications/<int:pk>/reject/', application_reject_view, name='application-reject'),
]
