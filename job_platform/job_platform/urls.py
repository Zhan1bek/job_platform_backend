from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

from chat.views import MessageViewSet
from users.views import CustomTokenObtainPairView  # кастомная авторизация

from django.conf import settings
from django.conf.urls.static import static

from resumes.views import ResumeViewSet
# from chat.views import ChatViewSet

router = routers.DefaultRouter()
# router.register(r'chats', ChatViewSet, basename='chats')
router.register(r"resumes", ResumeViewSet, "resume")
router.register(r'messages', MessageViewSet, basename='messages')


# router.register(r'messages', MessageViewSet, basename='messages')

urlpatterns = [
    path('admin/', admin.site.urls),

    # JWT авторизация
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Основные приложения
    path('api/users/', include('users.urls')),
    path('api/companies/', include('companies.urls')),
    path('api/jobs/', include('jobs.urls')),  # если jobs существует
    path('api/', include(router.urls)),       # chat API
    path('api/publications/', include('publications.urls')),
    path('api/', include('reports.urls')),
    path('api/chat/', include('chat.urls')),


]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)