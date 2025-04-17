from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class BorrowStatus(models.TextChoices):
    BORROWED = "borrowed", _("Borrowed")
    RETURNED = "returned", _("Returned")
