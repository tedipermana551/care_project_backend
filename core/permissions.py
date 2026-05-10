from rest_framework.permissions import BasePermission

class IsLinkedPartner(BasePermission):
    message = 'You must be linked to a partner to access this resource'

    def has_permission(self, request, view):
        try:
            return request.user.userprofile.partner is not None
        except Exception:
            return False