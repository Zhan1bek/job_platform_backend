from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from jobs.views import VacancyViewSet, ResumeViewSet, RequestViewSet, ReviewViewSet
from chat.views import ChatViewSet, MessageViewSet

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
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
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
