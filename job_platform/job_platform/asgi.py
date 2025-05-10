import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# ── 1. Указываем настройки ─────────────────────────────────────────────
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "job_platform.settings")

# ── 2. Явно запускаем Django, чтобы реестр приложений был готов ────────
django.setup()                 # <<< ключевой вызов

# ── 3. Создаём обычное ASGI‑приложение для HTTP ────────────────────────
django_asgi_app = get_asgi_application()

# ── 4. Теперь можно безопасно импортировать всё, что тянет модели ──────
import chat.routing             # noqa  (импорт после setup!)

# ── 5. Финальный ProtocolTypeRouter ─────────────────────────────────────
application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(
            URLRouter(chat.routing.websocket_urlpatterns)
        ),
    }
)
