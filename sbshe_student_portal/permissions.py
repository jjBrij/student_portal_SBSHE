# sbshe_student_portal/permissions.py

from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow admin users to edit,
    and others to read only
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to admin/staff users
        return request.user and request.user.is_staff

class IsAdminOrOwner(permissions.BasePermission):
    """
    Custom permission to allow admin users full access,
    and users to access their own data
    """
    def has_object_permission(self, request, view, obj):
        # Admin users have full access
        if request.user.is_staff:
            return True
        
        # Check if the object belongs to the user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False

class IsAdminUser(permissions.BasePermission):
    """
    Allows access only to admin users (is_staff=True)
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class IsAuthenticatedAndActive(permissions.BasePermission):
    """
    Allows access only to authenticated and active users
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_active