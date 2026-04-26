"""Reusable DRF permissions for role-based access control."""
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdmin(BasePermission):
    """Coordinator role only."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "admin")

class IsFieldAgent(BasePermission):
    """Field agent role only."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "field_agent")

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return bool(request.user and request.user.is_authenticated and request.user.role == "admin")
