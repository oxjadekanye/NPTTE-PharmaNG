"""Tenant-safe access rules for explorer APIs."""
from __future__ import annotations

import uuid
from typing import Any

from apps.core.roles import is_regulator_user
from apps.explorer.constants import AGGREGATE_IDS, REGULATOR_ONLY_AGGREGATES
from apps.tenancy.services.tenant import (
    get_active_organisation_id,
    get_user_membership_organisations,
    log_tenant_access_denied,
    user_can_access_organisation,
)


def is_aggregate_id(entity_id: str) -> bool:
    return entity_id in AGGREGATE_IDS


def aggregate_requires_regulator(entity_id: str) -> bool:
    return entity_id in REGULATOR_ONLY_AGGREGATES


def _parse_uuid(value: str) -> uuid.UUID | None:
    try:
        return uuid.UUID(str(value))
    except (ValueError, TypeError, AttributeError):
        return None


def assert_explorer_access(
    request,
    *,
    entity_type: str,
    entity_id: str,
    related_organisation_id: uuid.UUID | None = None,
    notification_recipient_id: uuid.UUID | None = None,
) -> tuple[bool, str]:
    """
    Returns (allowed, denial_reason).
    Logs cross-tenant denial via TenantAccessLog.
    """
    user = request.user
    if not user or not user.is_authenticated:
        return False, "authentication_required"

    if is_aggregate_id(entity_id):
        if aggregate_requires_regulator(entity_id) and not (is_regulator_user(user) or user.is_superuser):
            log_tenant_access_denied(
                request,
                organisation_id=get_active_organisation_id(request),
                detail=f"explorer aggregate denied: {entity_type}/{entity_id}",
            )
            return False, "aggregate_regulator_only"
        return True, ""

    if related_organisation_id:
        if user_can_access_organisation(user, related_organisation_id):
            return True, ""
        log_tenant_access_denied(
            request,
            organisation_id=related_organisation_id,
            detail=f"explorer entity denied: {entity_type}/{entity_id}",
        )
        return False, "organisation_scope"

    if notification_recipient_id is not None:
        if user.is_superuser or is_regulator_user(user):
            return True, ""
        if notification_recipient_id == user.id:
            return True, ""
        log_tenant_access_denied(
            request,
            detail=f"explorer notification denied: {entity_id}",
        )
        return False, "notification_recipient"

    # No org on record — allow regulators only (national records).
    if is_regulator_user(user) or user.is_superuser:
        return True, ""

    log_tenant_access_denied(request, detail=f"explorer national entity denied: {entity_type}/{entity_id}")
    return False, "regulator_required"


def user_org_ids(user) -> list[uuid.UUID]:
    return get_user_membership_organisations(user)


def assert_regional_explorer_access(request, *, region_state: str) -> tuple[bool, str]:
    user = request.user
    if is_regulator_user(user) or user.is_superuser:
        return True, ""
    region_norm = (region_state or "").strip().lower()
    from apps.organisations.models import Organisation

    for oid in user_org_ids(user):
        st = (
            Organisation.objects.filter(pk=oid)
            .values_list("state", flat=True)
            .first()
        )
        if st and st.strip().lower() == region_norm:
            return True, ""
    log_tenant_access_denied(request, detail=f"explorer regional denied: {region_state}")
    return False, "regional_scope"
