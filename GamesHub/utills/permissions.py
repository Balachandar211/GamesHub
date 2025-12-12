from rest_framework.permissions import BasePermission, SAFE_METHODS
from Support.models import Ticket
from rest_framework.exceptions import NotFound

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
    
class IsSuperuser(BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser
    
class IsAdminuser(BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff

class IsAdminOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.assigned_staff == request.user and request.user.is_authenticated and request.user.is_staff

class IsModelOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user and request.user.is_authenticated

class CanCommentOnTicket(BasePermission):
    def has_permission(self, request, view):
        ticket_id = view.kwargs.get("pk")
        try:
            ticket = Ticket.objects.get(pk=ticket_id)
        except Ticket.DoesNotExist:
            raise NotFound(f"Ticket with id {ticket_id} not found")

        user = request.user

        return user.is_authenticated and (ticket.user_id == user.id or (ticket.assigned_staff_id == user.id and user.is_staff))