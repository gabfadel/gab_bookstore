from faker import Faker
from django.core.management.base import BaseCommand
from apps.books.models import Book


class Command(BaseCommand):
    help = "Populate the Book database with fake data using a fixture file"

    def handle(self, *args, **options):
        fake = Faker()

        books_fixture = [
            {
                "title": fake.sentence(nb_words=4),
                "author": fake.name(),
                "isbn": fake.isbn13(),
                "copies": fake.random_int(min=1, max=10),
            }
            for _ in range(100)
        ]

        added, skipped = 0, 0
        for book_data in books_fixture:
            isbn = book_data.get("isbn", "").replace("-", "").strip()
            if not isbn or Book.objects.filter(isbn=isbn).exists():
                skipped += 1
                continue

            book_data.setdefault("copies", 1)
            try:
                Book.objects.create(**book_data)
                added += 1
            except Exception as ex:
                self.stderr.write(f"Error saving book {book_data.get('title')}: {ex}")

        self.stdout.write(f"Books added: {added}; skipped (duplicates): {skipped}")
