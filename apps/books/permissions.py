from __future__ import annotations

from rest_framework import permissions, request


class IsStaffOrReadOnly(permissions.BasePermission):
    def has_permission(self, req: request.Request, _: object) -> bool:
        return req.method in permissions.SAFE_METHODS or bool(
            req.user and req.user.is_staff
        )


class IsClientUser(permissions.BasePermission):
    def has_permission(self, req: request.Request, _: object) -> bool:
        user = req.user
        if not (user and user.is_authenticated and not user.is_staff):
            return False
        if hasattr(user, "user_type"):
            return user.user_type == "client"
        return True
