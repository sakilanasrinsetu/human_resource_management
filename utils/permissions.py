# import
from rest_framework.permissions import BasePermission
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from utils.response_wrapper import ResponseWrapper
User = get_user_model()


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser


class CheckCustomPermission(permissions.BasePermission):
    def __init__(self, perm_name: str) -> None:
        super().__init__()
        self.perm_name = perm_name

    def __call__(self):
        return self

    def has_permission(self, request, view):
        
        if request.user.is_superuser:
            return True
        elif self.perm_name:
            user = request.user
            if user.is_anonymous:
                return False
            permissions_qs = user.custom_permission.filter(codename=self.perm_name)
            if permissions_qs:
                return True
        else:
            return False

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.owner == request.user