from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from apps.users.choices import USER_TYPE_CHOICES


class User(AbstractUser):
    user_type = models.CharField(
        max_length=10, choices=USER_TYPE_CHOICES, default="client"
    )

    groups = models.ManyToManyField(
        Group,
        related_name="%(class)s_groups",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="%(class)s_user_permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )
