"""
Django settings for job_platform project.
Deploy‑friendly: SQLite → /data, WhiteNoise, Channels In‑Memory.
"""

from pathlib import Path
import os
from datetime import timedelta

# ─────────────────── Базовые пути ────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
PERSISTENT_DIR = Path(os.getenv("PERSISTENT_DIR", BASE_DIR))  # Render монтирует /data

# ─────────────────── Безопасность ─────────────────────
SECRET_KEY = os.getenv("DJANGO_SECRET", "dev-secret‑only‑for‑local")
DEBUG = os.getenv("DEBUG", "True") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

# ─────────────────── Приложения ───────────────────────
INSTALLED_APPS = [
    # core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 3‑rd party
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "drf_yasg",
    "django_filters",
    "corsheaders",
    "channels",
    "django_cleanup.apps.CleanupConfig",
    "whitenoise.runserver_nostatic",
    # local apps
    "users",
    "companies",
    "jobs",
    "resumes",
    "chat",
    "publications",
    "reports",
]

# ─────────────────── Middleware ───────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",      # ← static
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ─────────────────── URLs / Templates ─────────────────
ROOT_URLCONF = "job_platform.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "job_platform.wsgi.application"
ASGI_APPLICATION = "job_platform.asgi.application"

# ─────────────────── Channels ─────────────────────────
# На бесплатном Render отдельного Redis‑инстанса нет,
# поэтому временно используем In‑Memory слой (1‑процессовый).
CHANNEL_LAYERS = {
    "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}
}
# Когда подключите Redis (Render > Add‑ons > Redis) — верните конфиг channels_redis.

# ─────────────────── База данных ──────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(os.environ.get('PERSISTENT_DIR', '/data'), 'db.sqlite3'),
    }
}

# ─────────────────── Аутентификация ───────────────────
AUTH_USER_MODEL = "users.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
}
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=4),
}

LOGIN_REDIRECT_URL = "/api/users/dashboard/"

# ─────────────────── Локализация ──────────────────────
LANGUAGE_CODE = "ru-RU"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ─────────────────── Файлы ────────────────────────────
STATIC_URL = "/static/"
STATIC_ROOT = PERSISTENT_DIR / "static"     # WhiteNoise будет читать отсюда

MEDIA_URL = "/media/"
MEDIA_ROOT = PERSISTENT_DIR / "media"

# WhiteNoise: GZip + кеш‑заголовки
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ─────────────────── Разное ───────────────────────────
CORS_ALLOW_ALL_ORIGINS = True

PDFKIT_CONFIG = {"wkhtmltopdf": "/usr/local/bin/wkhtmltopdf"}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
