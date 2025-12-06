from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        else:
            return request.user and request.user.is_authenticated and request.user.is_staff

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        model = obj.__class__.__name__.lower()
        if request.user.is_authenticated and any(key in request.data for key in [f"downvote_{model}", f"upvote_{model}"]):
            return True

        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user and request.user.is_authenticated