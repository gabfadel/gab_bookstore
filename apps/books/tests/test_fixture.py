from django.test import TestCase
from django.utils import timezone
from .factories import UserFactory, StaffFactory, BookFactory, BorrowFactory


class FactoriesTestCase(TestCase):
    def test_user_factory(self):
        user = UserFactory()
        self.assertIsNotNone(user.pk)
        self.assertEqual(user.user_type, "client")
        self.assertNotEqual(user.password, "admin123")
        self.assertTrue(user.check_password("admin123"))

    def test_staff_factory(self):
        staff = StaffFactory()
        self.assertIsNotNone(staff.pk)
        self.assertEqual(staff.user_type, "staff")
        self.assertTrue(staff.is_staff)
        self.assertTrue(staff.is_superuser)
        self.assertTrue(staff.check_password("admin123"))

    def test_book_factory(self):
        book = BookFactory()
        self.assertIsNotNone(book.pk)
        self.assertTrue(book.isbn.startswith("9780000000"))
        self.assertTrue(book.title)
        self.assertTrue(book.author)
        self.assertTrue(book.description)
        published_year = str(book.published_date)
        self.assertEqual(len(published_year), 4)

    def test_borrow_factory(self):
        borrow = BorrowFactory()
        self.assertIsNotNone(borrow.pk)
        self.assertIsNotNone(borrow.due_date)
        self.assertGreater(borrow.due_date, timezone.now().date())
        self.assertIsNotNone(borrow.book)
        self.assertIsNotNone(borrow.user)
