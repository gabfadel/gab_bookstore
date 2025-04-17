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
        fields = ["isbn", "copies"]

    def validate_isbn(self, value: str) -> str:
        return value.replace("-", "")

    def create(self, validated_data: Dict[str, Any]) -> Book:
        isbn = validated_data["isbn"]
        google_data = fetch_google_books_info(isbn)

        to_fill = [
            "title",
            "author",
            "description",
            "published_date",
            "cover_thumbnail",
            "publisher",
            "page_count",
        ]
        for field in to_fill:
            if google_data.get(field):
                validated_data[field] = google_data[field]

        required = ["title", "author", "description", "published_date"]
        missing = [f for f in required if not validated_data.get(f)]
        if missing:
            raise serializers.ValidationError(
                {
                    "detail": (
                        "Mandatory fields missing or not found in Google Books API: "
                        f"{', '.join(missing)}"
                    )
                }
            )

        validated_data.setdefault("copies", 1)
        return Book.objects.create(**validated_data)


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
