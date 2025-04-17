# Generated by Django 4.2 on 2025-04-17 13:29

from django.db import migrations
from apps.books.management.commands.populate_book import Command as PopulateBookCommand


def populate_books(apps, schema_editor):
    cmd = PopulateBookCommand()
    cmd.handle()


class Migration(migrations.Migration):

    dependencies = [
        ("books", "0001_initial"),
    ]

    operations = [
                migrations.RunPython(
            populate_books,
            reverse_code=migrations.RunPython.noop  
        ),
    ]
