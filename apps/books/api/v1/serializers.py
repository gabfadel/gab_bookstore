from __future__ import annotations

from typing import Any, Dict


from rest_framework import serializers

from apps.books.models import Book, Borrow
from apps.books.utils import fetch_google_books_info


class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            "id",
            "isbn",
            "title",
            "author",
            "description",
            "published_date",
            "cover_thumbnail",
            "publisher",
            "page_count",
            "copies",
        ]


class BookDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            "id",
            "isbn",
            "title",
            "author",
            "description",
            "published_date",
            "cover_thumbnail",
            "publisher",
            "page_count",
            "copies",
        ]


class BookCreateSerializer(serializers.ModelSerializer):
    isbn = serializers.CharField(max_length=20)

    class Meta:
        model = Book
        fields = [
            "isbn",
            "title",
            "author",
            "description",
            "published_date",
        ]

    def validate_copies(self, value: int) -> int:
        if value < 0:
            raise serializers.ValidationError("copies must be ≥ 0.")
        return value

    def validate_isbn(self, value):
        return value.replace("-", "")

    def create(self, validated: Dict[str, Any]) -> Book:
        isbn = validated.get("isbn")

        clean_isbn = isbn.replace("-", "") if isbn else ""

        google = fetch_google_books_info(clean_isbn) if clean_isbn else {}

        for field in [
            "title",
            "author",
            "description",
            "published_date",
            "cover_thumbnail",
            "publisher",
            "page_count",
        ]:
            validated.setdefault(field, google.get(field))

        if not validated.get("title"):
            raise serializers.ValidationError("Title missing and not found via ISBN.")
        return Book.objects.create(**validated)


class BorrowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrow
        fields = [
            "id",
            "user",
            "book",
            "status",
            "borrowed_at",
            "due_date",
            "returned_at",
        ]
        read_only_fields = fields
