from __future__ import annotations

from datetime import timedelta
from django.db import models, transaction
from django.db.models import F
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from apps.books.models import Book, Borrow
from apps.books.permissions import IsClientUser
from apps.books.choices import BorrowStatus
from apps.books.api.v1.serializers import (
    BookListSerializer,
    BookDetailSerializer,
    BookCreateSerializer,
    BorrowSerializer,
)

CACHE_ONE_HOUR = cache_page(60 * 60)


@method_decorator(CACHE_ONE_HOUR, name="retrieve")
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().prefetch_related(
        models.Prefetch("borrows", queryset=Borrow.objects.select_related("user"))
    )
    http_method_names = ["get", "post", "delete", "options", "head"]

    def get_serializer_class(self):
        if self.action == "create":
            return BookCreateSerializer
        elif self.action == "list":
            return BookListSerializer
        elif self.action in ("borrow", "return_it"):
            return
        return BookDetailSerializer

    @swagger_auto_schema(request_body=None)
    @method_decorator(CACHE_ONE_HOUR)
    def list(self, request: Request, *args, **kwargs) -> Response:
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=BookCreateSerializer,
        responses={200: BookDetailSerializer, 400: "Bad Request"},
    )
    def create(self, request: Request, *args, **kwargs) -> Response:
        if not (request.user and request.user.user_type == "staff"):
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        book = serializer.save()
        out = BookDetailSerializer(book)
        headers = self.get_success_headers(out.data)
        return Response(out.data, status=status.HTTP_200_OK, headers=headers)

    @swagger_auto_schema(request_body=None, responses={200: BorrowSerializer})
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated, IsClientUser],
    )
    def borrow(self, request: Request, pk: str | None = None) -> Response:
        book: Book = self.get_object()
        with transaction.atomic():
            updated = Book.objects.filter(pk=book.pk, copies__gt=0).update(
                copies=F("copies") - 1
            )
            if updated == 0:
                return Response({"detail": "No copies available."}, status=400)
            borrow = Borrow.objects.create(
                user=request.user,
                book=book,
                due_date=timezone.now().date() + timedelta(days=14),
            )
        return Response(BorrowSerializer(borrow).data, status=200)

    @swagger_auto_schema(request_body=None)
    @action(
        detail=True,
        methods=["post"],
        url_path="return_it",
        permission_classes=[permissions.IsAuthenticated, IsClientUser],
    )
    def return_it(self, request: Request, pk: str | None = None) -> Response:
        book = self.get_object()
        try:
            borrow = Borrow.objects.get(
                user=request.user,
                book=book,
                status=BorrowStatus.BORROWED,
            )
        except Borrow.DoesNotExist:
            return Response(
                {"detail": "No active borrow for this book."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        borrow.mark_returned()
        return Response(BorrowSerializer(borrow).data)
