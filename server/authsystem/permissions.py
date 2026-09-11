from rest_framework.permissions import BasePermission


class IsAdminUserRole(BasePermission):
    """Allows access only to Admin users."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_admin()
        )


class IsStaffUserRole(BasePermission):
    """Allows access to Staff members and Admins."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff_member() or request.user.is_admin())
        )
