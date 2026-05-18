"""Phase 14 — tenant-aware DRF permissions."""
from rest_framework.permissions import BasePermission

from apps.core.roles import is_regulator_user
from apps.tenancy.services.tenant import log_tenant_access_denied, user_can_access_organisation


class HasTenantOrganisationAccess(BasePermission):
    """Deny cross-tenant access when organisation_id is supplied in URL/body."""

    message = "Organisation access denied."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if is_regulator_user(user) or user.is_superuser:
            return True
        org_id = (
            request.data.get("organisation_id")
            or request.query_params.get("organisation_id")
            if hasattr(request, "query_params")
            else None
        )
        if org_id and not user_can_access_organisation(user, org_id):
            log_tenant_access_denied(request, organisation_id=org_id, detail="cross_tenant_permission")
            return False
        return bool(getattr(request, "nptte_organisation_id", None) or user.organisation_id)
