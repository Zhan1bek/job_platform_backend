from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from jobs.views import VacancyViewSet, ResumeViewSet, RequestViewSet, ReviewViewSet
from chat.views import ChatViewSet, MessageViewSet

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
]
