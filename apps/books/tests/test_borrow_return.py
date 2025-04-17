from rest_framework import status
from .factories import (
    UserFactory,
    StaffFactory,
    BookFactory,
    UserFactory2,
)
from .auth_utils import JWTAuthMixin
from apps.books.models import Borrow


class BookBorrowReturnTests(JWTAuthMixin):
    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.user2 = UserFactory2()  # User with user_type="staff" but is_staff=False
        self.other = UserFactory()
        self.staff = StaffFactory()  # User with user_type="staff" and is_staff=True
        self.book = BookFactory()
        self.borrow_url = f"/v1/books/books/{self.book.id}/borrow/"
        self.return_url = f"/v1/books/books/{self.book.id}/return_it/"

    def test_borrow_requires_client(self):
        self.assertEqual(self.client.post(self.borrow_url).status_code, 401)

        self.authenticate_as(self.staff)
        self.assertEqual(self.client.post(self.borrow_url).status_code, 403)

        self.authenticate_as(self.user)
        ok = self.client.post(self.borrow_url)
        self.assertEqual(ok.status_code, 200)
        self.assertTrue(Borrow.objects.filter(user=self.user, book=self.book).exists())

    def test_borrow_and_return_happy_path(self):
        self.authenticate_as(self.user)
        self.client.post(self.borrow_url)

        returned = self.client.post(self.return_url)
        self.assertEqual(returned.status_code, 200)
        borrow = Borrow.objects.get(user=self.user, book=self.book)
        self.assertEqual(borrow.status, "returned")

    def test_return_without_borrow(self):
        self.authenticate_as(self.other)
        self.assertEqual(self.client.post(self.return_url).status_code, 400)
