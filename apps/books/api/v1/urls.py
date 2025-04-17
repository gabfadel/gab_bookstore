from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.books.api.v1.views import BookViewSet

router = DefaultRouter()
router.register("books", BookViewSet, basename="book")

urlpatterns = [path("", include(router.urls))]
