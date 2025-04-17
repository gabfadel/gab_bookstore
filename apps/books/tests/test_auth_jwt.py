from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .factories import UserFactory, StaffFactory

User = get_user_model()


class TestAuthJWT(APITestCase):
    RAW_PASSWORD = "admin123"

    def setUp(self):
        self.user = UserFactory(password=self.RAW_PASSWORD)
        self.staff = StaffFactory(password=self.RAW_PASSWORD)
        self.login_url = "/v1/auth/login/"
        self.refresh_url = "/v1/auth/refresh/"
        self.blacklist_url = "/v1/auth/blacklist/"
        self.books_list = "/v1/books/books/"

    def test_login_valid_and_invalid(self):
        r1 = self.client.post(
            self.login_url,
            {"username": self.staff.username, "password": "wrong"},
            format="json",
        )
        self.assertEqual(r1.status_code, status.HTTP_401_UNAUTHORIZED)

        r2 = self.client.post(
            self.login_url,
            {"username": self.staff.username, "password": self.RAW_PASSWORD},
            format="json",
        )
        self.assertEqual(r2.status_code, status.HTTP_200_OK)
        data = r2.json()
        self.assertIn("access", data)
        self.assertIn("refresh", data)

    def test_protected_route_requires_token(self):
        r1 = self.client.post(self.books_list, {"isbn": "1234567890123"}, format="json")
        self.assertEqual(r1.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_protected_route_with_token(self):
        login = self.client.post(
            self.login_url,
            {"username": self.staff.username, "password": self.RAW_PASSWORD},
            format="json",
        )
        token = login.json()["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        r2 = self.client.get(self.books_list)
        self.assertEqual(r2.status_code, status.HTTP_200_OK)

    def test_create_book_requires_staff(self):
        isbn = "1234567890123"

        login = self.client.post(
            self.login_url,
            {"username": self.user.username, "password": self.RAW_PASSWORD},
            format="json",
        )
        token = login.json()["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        res_client = self.client.post(self.books_list, {"isbn": isbn}, format="json")
        self.assertEqual(res_client.status_code, status.HTTP_403_FORBIDDEN)
