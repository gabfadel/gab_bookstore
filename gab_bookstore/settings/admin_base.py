"""
Base settings for the Admin.
"""

from .base import *  # noqa: F403,F401

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third-party apps
    # add your apps here
    "apps.books",
    "apps.users",
    "apps.core",
]

ROOT_URLCONF = "gab_bookstore.admin_urls"
WSGI_APPLICATION = "gab_bookstore.wsgi.application"
