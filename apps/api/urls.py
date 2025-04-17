from django.urls import include, path
from rest_framework import routers
from apps.api import views

router = routers.DefaultRouter()

urlpatterns = [
    path("v1/", include(("apps.api.v1.urls", "apps.api.v1"), namespace="v1")),
    path("status/", views.health_check, name="health-check"),
] + router.urls
