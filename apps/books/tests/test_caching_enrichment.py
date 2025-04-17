# apps/books/tests/test_caching_enrichment.py
from __future__ import annotations

from django.core.cache import cache
from django.contrib.auth import get_user_model
from unittest.mock import patch
from apps.books.tests.auth_utils import JWTAuthMixin
from faker import Faker

from apps.books.models import Book
from apps.books.utils import fetch_google_books_info
from .factories import UserFactory, StaffFactory

fake = Faker()
User = get_user_model()


class TestCachingEnrichment(JWTAuthMixin):
    RAW_PASSWORD = "admin123"

    def setUp(self):
        super().setUp()
        cache.clear()
        self.staff = StaffFactory()
        self.client_user = UserFactory()
        self.books_url = "/v1/books/books/"

    def _resp_dummy(self, data):
        class Resp:
            def __init__(self, d):
                self._d = d

            def json(self):
                return self._d

            def raise_for_status(self): ...

        return Resp(data)

    def test_fetch_google_books_info_cache(self):
        isbn = fake.isbn13(separator="")
        payload = {
            "items": [
                {
                    "volumeInfo": {
                        "title": "X",
                        "authors": ["A", "B"],
                        "publishedDate": "2020",
                        "imageLinks": {"thumbnail": "http://ex.com/img.jpg"},
                        "publisher": "P",
                        "pageCount": 100,
                        "description": "D",
                    }
                }
            ]
        }

        with patch(
            "apps.books.utils.requests.get", return_value=self._resp_dummy(payload)
        ) as mock_get:
            r1 = fetch_google_books_info(isbn)
            r2 = fetch_google_books_info(isbn)
            mock_get.assert_called_once()
            self.assertEqual(r1, r2)
            self.assertEqual(r1["title"], "X")
            self.assertEqual(r1["author"], "A, B")
            self.assertEqual(r1["cover_thumbnail"], "http://ex.com/img.jpg")

    def test_create_book_with_enrichment(self):
        isbn = fake.isbn13(separator="")
        enriched = {
            "title": "E",
            "author": "Z",
            "published_date": "2021",
            "publisher": "Pub",
            "page_count": 200,
            "description": "Desc",
            "cover_thumbnail": "http://ex.com/c.jpg",
        }

        with patch(
            "apps.books.api.v1.serializers.fetch_google_books_info",
            return_value=enriched,
        ) as mock_fetch:

            self.authenticate_as(self.client_user)
            res_client = self.client.post(self.books_url, {"isbn": isbn}, format="json")
            self.assertEqual(res_client.status_code, 403)

            self.authenticate_as(self.staff)
            res_staff = self.client.post(self.books_url, {"isbn": isbn}, format="json")
            self.assertEqual(res_staff.status_code, 200)
            data = res_staff.json()
            self.assertEqual(data["title"], enriched["title"])
            self.assertTrue(Book.objects.filter(isbn=isbn, publisher="Pub").exists())
            mock_fetch.assert_called_once_with(isbn)

    def test_create_book_enrichment_fail(self):
        isbn = fake.isbn13(separator="")

        with patch(
            "apps.books.api.v1.serializers.fetch_google_books_info", return_value={}
        ) as mock_fetch:

            self.authenticate_as(self.staff)
            res = self.client.post(self.books_url, {"isbn": isbn}, format="json")
            self.assertEqual(res.status_code, 400)
            self.assertFalse(Book.objects.filter(isbn=isbn).exists())
            mock_fetch.assert_called_once_with(isbn)
