from rest_framework import permissions


class IsAdminOrPublicCreate(permissions.BasePermission):
    """
    Custom permission:
    - Allow any user to create and submit forms (POST)
    - Allow any user to view forms (GET)
    - Only admins can update, delete, or perform other actions
    """
    def has_permission(self, request, view):
        # Allow GET requests (view) for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Allow POST requests to create and submit
        if request.method == 'POST':
            # Check if it's the submit action
            if view.action == 'submit':
                return True
            # Allow creation of new forms
            if view.action == 'create':
                return True
            # Allow listing
            if view.action == 'list':
                return True
        
        # For other methods (PUT, PATCH, DELETE), require admin
        return request.user and request.user.is_staff