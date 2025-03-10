from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from jobs.views import VacancyViewSet, ResumeViewSet, RequestViewSet, ReviewViewSet
from chat.views import ChatViewSet, MessageViewSet


schema_view = get_schema_view(
    openapi.Info(
        title="Job Platform API",
        default_version='v1',
        description="API documentation for Job Platform",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@jobplatform.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = routers.DefaultRouter()
router.register(r'vacancies', VacancyViewSet)
router.register(r'resumes', ResumeViewSet)
router.register(r'requests', RequestViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'chats', ChatViewSet)
router.register(r'messages', MessageViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include([
        path('', include(router.urls)),
        path('users/', include('users.urls')),
    ])),


    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]