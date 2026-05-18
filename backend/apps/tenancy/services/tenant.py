"""Phase 14 — tenant context resolution and queryset scoping."""
from __future__ import annotations

import uuid

from django.db.models import Q, QuerySet
from django.utils import timezone

from apps.core.roles import is_regulator_user
from apps.tenancy.models import OrganisationContextSwitch, OrganisationMembership, TenantAccessLog


def get_user_membership_organisations(user) -> list[uuid.UUID]:
    if not user or not user.is_authenticated:
        return []
    ids = list(
        OrganisationMembership.objects.filter(
            user=user,
            membership_status=OrganisationMembership.STATUS_ACTIVE,
        ).values_list("organisation_id", flat=True)
    )
    if user.organisation_id and user.organisation_id not in ids:
        ids.append(user.organisation_id)
    return ids


def resolve_request_organisation_id(request) -> uuid.UUID | None:
    """Active tenant: header override (regulators), query param, membership, or user.organisation."""
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return None

    header_org = request.META.get("HTTP_X_NPTTE_ORGANISATION_CONTEXT")
    if header_org and is_regulator_user(user):
        try:
            return uuid.UUID(str(header_org))
        except (ValueError, TypeError):
            pass

    query_org = request.GET.get("organisation_id")
    if hasattr(request, "query_params"):
        query_org = query_org or request.query_params.get("organisation_id")
    if query_org and is_regulator_user(user):
        try:
            return uuid.UUID(str(query_org))
        except (ValueError, TypeError):
            pass

    cached = getattr(request, "nptte_organisation_id", None)
    if cached:
        return cached

    if user.organisation_id:
        return user.organisation_id

    memberships = get_user_membership_organisations(user)
    return memberships[0] if memberships else None


def get_active_organisation_id(request) -> uuid.UUID | None:
    return resolve_request_organisation_id(request)


def regulator_can_access_organisation(user, organisation_id) -> bool:
    return is_regulator_user(user) or user.is_superuser


def user_can_access_organisation(user, organisation_id) -> bool:
    if not organisation_id:
        return False
    if regulator_can_access_organisation(user, organisation_id):
        return True
    if user.organisation_id == organisation_id:
        return True
    return OrganisationMembership.objects.filter(
        user=user,
        organisation_id=organisation_id,
        membership_status=OrganisationMembership.STATUS_ACTIVE,
    ).exists()


def filter_queryset_for_tenant(
    request,
    queryset: QuerySet,
    *,
    org_field: str = "organisation_id",
    allow_null: bool = False,
) -> QuerySet:
    user = request.user
    if is_regulator_user(user) or user.is_superuser:
        org_id = resolve_request_organisation_id(request)
        if org_id:
            return queryset.filter(**{org_field: org_id})
        return queryset

    org_ids = get_user_membership_organisations(user)
    if not org_ids:
        return queryset.none()

    q = Q(**{f"{org_field}__in": org_ids})
    if allow_null:
        q |= Q(**{f"{org_field}__isnull": True})
    return queryset.filter(q)


def log_tenant_access_denied(request, *, organisation_id=None, detail: str = "") -> None:
    TenantAccessLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        attempted_organisation_id=organisation_id,
        path=getattr(request, "path", "")[:512],
        event_type="access_denied",
        detail=detail[:2000],
        client_ip=request.META.get("REMOTE_ADDR"),
    )


def set_regulator_context(*, actor, organisation_id, reason: str = "") -> OrganisationContextSwitch:
    OrganisationContextSwitch.objects.filter(actor=actor, is_active=True).update(
        is_active=False, ended_at=timezone.now()
    )
    return OrganisationContextSwitch.objects.create(
        actor=actor,
        organisation_id=organisation_id,
        reason=reason,
        created_by=actor,
    )
