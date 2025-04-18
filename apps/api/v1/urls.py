from django.urls import include, path

urlpatterns = [
    # /api/v1/
    path(
        "auth/",
        include(("apps.users.api.v1.urls", "apps.users.api.v1"), namespace="auth"),
    ),
    path(
        "books/",
        include(("apps.books.api.v1.urls", "apps.books.api.v1"), namespace="books"),
    ),
]
