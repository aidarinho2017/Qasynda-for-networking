from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Allow read to anyone. Allow write only if request.user == obj.organizer.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions only for the organizer
        return hasattr(obj, 'organizer') and obj.organizer == request.user