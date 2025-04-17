from __future__ import annotations


from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

from apps.books.choices import BorrowStatus


class Book(models.Model):

    isbn = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=255)
    author = models.CharField(
        max_length=255,
    )
    description = models.TextField()
    published_date = models.CharField(max_length=20)
    cover_thumbnail = models.URLField(blank=True, null=True)
    publisher = models.CharField(max_length=255, blank=True, null=True)
    page_count = models.PositiveIntegerField(blank=True, null=True)
    copies = models.PositiveIntegerField(default=1)

    def __str__(self) -> str:
        return f"{self.title} ({self.isbn})"


class Borrow(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrows")
    status = models.CharField(
        max_length=8,
        choices=BorrowStatus.choices,
        default=BorrowStatus.BORROWED,
    )
    borrowed_at = models.DateTimeField(default=timezone.now)
    due_date = models.DateField()
    returned_at = models.DateTimeField(blank=True, null=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.user} – {self.book} ({self.status})"

    # ------------------------------ business logic -------------------------- #
    @transaction.atomic
    def mark_returned(self) -> None:
        if self.status == BorrowStatus.RETURNED:
            return
        self.status = BorrowStatus.RETURNED
        self.returned_at = timezone.now()
        self.save(update_fields=["status", "returned_at"])
        self.book.copies = models.F("copies") + 1
        self.book.save(update_fields=["copies"])
