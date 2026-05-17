"""Enterprise organisation onboarding workflows."""
from __future__ import annotations

from django.utils import timezone

from apps.audit.services import log_api_action
from apps.core.constants import OnboardingStatus, RecordStatus
from apps.onboarding.models import ApprovalWorkflow, OrganisationOnboarding


def approve_organisation(*, onboarding: OrganisationOnboarding, actor, request=None, notes: str = "") -> OrganisationOnboarding:
    onboarding.status = OnboardingStatus.APPROVED
    onboarding.reviewed_at = timezone.now()
    onboarding.save(update_fields=["status", "reviewed_at", "updated_at"])
    org = onboarding.organisation
    org.status = RecordStatus.ACTIVE
    org.is_active = True
    org.save(update_fields=["status", "is_active", "updated_at"])
    ApprovalWorkflow.objects.create(
        onboarding=onboarding,
        step_name="final_approval",
        completed_at=timezone.now(),
        is_approved=True,
        created_by=actor,
    )
    log_api_action(
        request=request,
        actor=actor,
        action="onboarding.approve",
        entity_type="organisation_onboarding",
        entity_id=onboarding.id,
        after_state={"status": onboarding.status, "notes": notes},
    )
    return onboarding


def reject_organisation(
    *, onboarding: OrganisationOnboarding, actor, reason: str, request=None
) -> OrganisationOnboarding:
    onboarding.status = OnboardingStatus.REJECTED
    onboarding.rejection_reason = reason
    onboarding.reviewed_at = timezone.now()
    onboarding.save(update_fields=["status", "rejection_reason", "reviewed_at", "updated_at"])
    log_api_action(
        request=request,
        actor=actor,
        action="onboarding.reject",
        entity_type="organisation_onboarding",
        entity_id=onboarding.id,
        after_state={"status": onboarding.status, "reason": reason},
    )
    return onboarding


def request_compliance_review(*, onboarding: OrganisationOnboarding, actor, request=None) -> OrganisationOnboarding:
    onboarding.status = OnboardingStatus.UNDER_REVIEW
    onboarding.save(update_fields=["status", "updated_at"])
    ApprovalWorkflow.objects.create(
        onboarding=onboarding,
        step_name="compliance_review",
        assigned_regulator_role="NAFDAC_ADMIN",
        created_by=actor,
    )
    log_api_action(
        request=request,
        actor=actor,
        action="onboarding.compliance_review",
        entity_type="organisation_onboarding",
        entity_id=onboarding.id,
    )
    return onboarding
