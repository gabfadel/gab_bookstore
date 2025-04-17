"""
Base settings for the API.
"""

from .base import *  # noqa: F403

# API-specific apps
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third-party apps
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_yasg",
    "celery",
    "django_celery_beat",
    # add your apps here
    "apps.api",
    "apps.books",
    "apps.users",
]

ROOT_URLCONF = "gab_bookstore.api_urls"
WSGI_APPLICATION = "gab_bookstore.wsgi.application"

# Celery settings
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = CELERY_BROKER_URL

# Swagger settings
SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. "
            "Example: 'Authorization: Bearer {token}'",
        }
    },
}
