from rest_framework.test import APITestCase
from rest_framework import status
from .factories import UserFactory, BookFactory
from apps.books.models import Book
import json
from django.contrib.auth import get_user_model

User = get_user_model()


class BookCRUDTests(APITestCase):
    def setUp(self):
        staff = User.objects.create_user(
            username="staffuser",
            password="admin123",
            email="staff@example.com",
            is_staff=True,
        )
        self.client_user = UserFactory()
        self.list_url = "/v1/books/books/"
        self.book = BookFactory()
        self.login_url = "/v1/auth/login/"

        client_response = self.client.post(
            self.login_url,
            {"username": self.client_user.username, "password": "admin123"},
            format="json",
        )
        self.client_token = client_response.json()["access"]

        staff_response = self.client.post(
            self.login_url,
            {"username": staff.username, "password": "admin123"},
            format="json",
        )
        self.staff_token = staff_response.json()["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.client_token}")

    def test_list_books_does_not_requires_auth(self):
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.client_token}")
        res2 = self.client.get(f"{self.list_url}")
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        contains_number = any(char.isdigit() for char in json.dumps(res2.json()))
        self.assertTrue(contains_number)

    def test_create_client_delete_book(self):

        detail = f"/v1/books/books/{self.book.id}/"
        res_del = self.client.delete(detail)
        self.assertIn(
            res_del.status_code, (status.HTTP_204_NO_CONTENT, status.HTTP_200_OK)
        )
        self.assertFalse(Book.objects.filter(id=self.book.id).exists())


class BookBorrowReturnTests(APITestCase):
    def setUp(self):
        self.user = UserFactory()

        self.book = BookFactory()
        self.borrow_url = f"/v1/books/books/{self.book.id}/borrow/"
        self.return_url = f"/v1/books/books/{self.book.id}/return_it/"

        login_response = self.client.post(
            "/v1/auth/login/",
            {"username": self.user.username, "password": "admin123"},
            format="json",
        )
        self.user_token = login_response.json()["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

    def test_successful_borrow(self):
        res = self.client.post(self.borrow_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_borrow_nonexistent_book(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        nonexistent_url = f"/v1/books/books/999999/borrow/"
        res = self.client.post(nonexistent_url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_successful_return(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        borrow_res = self.client.post(self.borrow_url)
        self.assertEqual(borrow_res.status_code, status.HTTP_200_OK)
        return_res = self.client.post(self.return_url)
        self.assertEqual(return_res.status_code, status.HTTP_200_OK)


class TestAuthJWT(APITestCase):
    def setUp(self):
        self.login_url = "/v1/auth/login/"
        self.refresh_url = "/v1/auth/refresh/"
        self.protected_url = "/v1/books/books/"
        self.user = UserFactory()

    def test_refresh_token(self):
        login_payload = {"username": self.user.username, "password": "admin123"}
        login_res = self.client.post(self.login_url, login_payload, format="json")
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)

        refresh_token = login_res.json().get("refresh")
        refresh_res = self.client.post(
            self.refresh_url, {"refresh": refresh_token}, format="json"
        )
        self.assertEqual(refresh_res.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_res.json())
