import factory
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.books.models import Book, Borrow

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    user_type = "client"
    is_staff = False
    is_superuser = False
    is_active = True
    password = factory.PostGenerationMethodCall("set_password", "admin123")


class UserFactory2(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    user_type = "staff"
    is_staff = False
    is_superuser = False
    is_active = True
    password = factory.PostGenerationMethodCall("set_password", "admin123")


class StaffFactory(UserFactory):
    is_staff = True
    is_superuser = True
    user_type = "staff"


class BookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Book

    isbn = factory.Sequence(lambda n: f"9780000000{n:05d}")
    title = factory.Faker("sentence", nb_words=4)
    author = factory.Faker("name")
    description = factory.Faker("paragraph")
    published_date = factory.Faker("year")


class BorrowFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Borrow

    user = factory.SubFactory(UserFactory)
    book = factory.SubFactory(BookFactory)
    due_date = factory.LazyFunction(lambda: timezone.now().date() + timedelta(days=14))
    returned_at = None
