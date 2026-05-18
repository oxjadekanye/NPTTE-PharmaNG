"""Phase 14 — regulator approval queues and enforcement."""
from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.core.constants import OnboardingStatus, RecordStatus
from apps.onboarding.models import ApprovalWorkflow, OrganisationOnboarding
from apps.onboarding.services import approve_organisation, reject_organisation
from apps.organisations.models import Organisation
from apps.tenancy.services.onboarding import ensure_membership_for_user, ROLE_FOR_ORG_TYPE


def list_regulator_approval_queue(*, status: str | None = None) -> list[dict]:
    qs = OrganisationOnboarding.objects.select_related("organisation", "organisation_type").order_by(
        "-submitted_at", "-created_at"
    )
    if status:
        qs = qs.filter(status=status)
    else:
        qs = qs.filter(status__in=[OnboardingStatus.SUBMITTED, OnboardingStatus.UNDER_REVIEW])
    return [
        {
            "id": str(o.id),
            "organisation_id": str(o.organisation_id),
            "legal_name": o.organisation.legal_name,
            "organisation_type": o.organisation_type.code,
            "status": o.status,
            "submitted_at": o.submitted_at.isoformat() if o.submitted_at else None,
            "metadata": o.organisation.metadata,
        }
        for o in qs[:100]
    ]


@transaction.atomic
def approve_onboarding_application(*, onboarding_id, actor, notes: str = "") -> dict:
    onboarding = OrganisationOnboarding.objects.select_related("organisation").get(pk=onboarding_id)
    approve_organisation(onboarding=onboarding, actor=actor, notes=notes)
    ApprovalWorkflow.objects.create(
        onboarding=onboarding,
        step_name="regulator_approval",
        is_approved=True,
        completed_at=timezone.now(),
        created_by=actor,
    )
    org_type = onboarding.organisation.metadata.get("onboarding_org_type", "manufacturer")
    role_code = ROLE_FOR_ORG_TYPE.get(org_type, "ORGANISATION_STAFF")
    if actor and actor.organisation_id == onboarding.organisation_id:
        ensure_membership_for_user(user=actor, organisation=onboarding.organisation, role_code=role_code)
    return {"status": onboarding.status, "organisation_id": str(onboarding.organisation_id)}


@transaction.atomic
def reject_onboarding_application(*, onboarding_id, actor, reason: str) -> dict:
    onboarding = OrganisationOnboarding.objects.get(pk=onboarding_id)
    reject_organisation(onboarding=onboarding, actor=actor, reason=reason)
    return {"status": onboarding.status, "reason": reason}


@transaction.atomic
def suspend_organisation(*, organisation_id, actor, reason: str = "") -> Organisation:
    org = Organisation.objects.get(pk=organisation_id)
    org.is_active = False
    org.status = RecordStatus.SUSPENDED
    org.metadata = {**(org.metadata or {}), "suspension_reason": reason}
    org.save(update_fields=["is_active", "status", "metadata", "updated_at"])
    OrganisationOnboarding.objects.filter(organisation=org).update(status=OnboardingStatus.REJECTED)
    return org


@transaction.atomic
def reactivate_organisation(*, organisation_id, actor) -> Organisation:
    org = Organisation.objects.get(pk=organisation_id)
    org.is_active = True
    org.status = RecordStatus.ACTIVE
    org.save(update_fields=["is_active", "status", "updated_at"])
    return org
