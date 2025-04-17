import os
from django.contrib import admin
from django.urls import path, include

SERVER_TYPE = os.getenv("SERVER_TYPE", "api")

if SERVER_TYPE == "admin":
    urlpatterns = [
        path("admin/", admin.site.urls),
    ]
else:
    urlpatterns = [
        path("", include("apps.api.urls")),
    ]
