from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


class CustomUserAdmin(BaseUserAdmin):
    list_display = BaseUserAdmin.list_display + ("user_type",)
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("user_type",)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + ((None, {"fields": ("user_type",)}),)


admin.site.register(User, CustomUserAdmin)
