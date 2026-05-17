"""
Cross-cutting permission placeholders for NPTTE.

Role-based access control will be enforced via DRF permissions and
organisation-scoped policies in later phases.
"""
from rest_framework.permissions import BasePermission


class IsRegulatorUser(BasePermission):
    """Placeholder: allow users linked to a regulator organisation."""

    message = "Regulator access required."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "is_regulator", False)
        )


class IsOrganisationMember(BasePermission):
    """Placeholder: allow members of the target organisation."""

    message = "Organisation membership required."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
