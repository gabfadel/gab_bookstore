import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gab_bookstore.settings.api_local")

app = Celery("gab_bookstore")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
