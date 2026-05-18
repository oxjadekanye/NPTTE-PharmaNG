"""Phase 15 hooks for tenancy and onboarding events."""
from django.conf import settings

from apps.notifications.constants import (
    NOTIFICATION_TYPE_APPROVAL,
    NOTIFICATION_TYPE_INVITATION,
    NOTIFICATION_TYPE_ONBOARDING,
    SEVERITY_INFO,
    SEVERITY_SUCCESS,
    SEVERITY_WARNING,
)
from apps.notifications.email_service import send_platform_email
from apps.notifications.services.delivery import (
    deliver_notification,
    notify_organisation_admins,
    render_invitation_email,
)
from apps.operations.models import RegulatorOperationalHistory, WorkflowTimelineEntry
from apps.operations.services.tasks import create_operational_task
from apps.operations.services.workflow import record_regulator_action, record_workflow_event


def on_invitation_created(*, invitation, invited_by) -> None:
    accept_url = f"{settings.NPTTE_FRONTEND_URL}/onboarding/accept?token={invitation.token}"
    subject, body = render_invitation_email(
        organisation_name=invitation.organisation.legal_name,
        role_name=invitation.role.name if invitation.role else "staff",
        accept_url=accept_url,
    )
    send_platform_email(subject=subject, message=body, recipient_list=[invitation.email])
    record_workflow_event(
        workflow_type=WorkflowTimelineEntry.WORKFLOW_INVITATION,
        title="Invitation sent",
        summary=invitation.email,
        organisation=invitation.organisation,
        actor=invited_by,
        entity_type="organisation_invitation",
        entity_id=invitation.id,
        created_by=invited_by,
    )


def on_invitation_accepted(*, invitation, user) -> None:
    deliver_notification(
        recipient=user,
        title=f"Welcome to {invitation.organisation.legal_name}",
        body="Your organisation membership is now active.",
        severity=SEVERITY_SUCCESS,
        notification_type=NOTIFICATION_TYPE_INVITATION,
        organisation=invitation.organisation,
        send_email=bool(user.email),
        created_by=invitation.invited_by,
    )
    record_workflow_event(
        workflow_type=WorkflowTimelineEntry.WORKFLOW_INVITATION,
        title="Invitation accepted",
        summary=user.username,
        organisation=invitation.organisation,
        actor=user,
        entity_type="organisation_invitation",
        entity_id=invitation.id,
        created_by=user,
    )


def on_onboarding_submitted(*, onboarding, actor=None) -> None:
    notify_organisation_admins(
        organisation=onboarding.organisation,
        title="Onboarding submitted for regulator review",
        body="Your application is pending approval.",
        severity=SEVERITY_INFO,
        notification_type=NOTIFICATION_TYPE_ONBOARDING,
        created_by=actor,
    )
    record_workflow_event(
        workflow_type=WorkflowTimelineEntry.WORKFLOW_ONBOARDING,
        title="Onboarding submitted",
        organisation=onboarding.organisation,
        actor=actor,
        entity_type="organisation_onboarding",
        entity_id=onboarding.id,
        created_by=actor,
    )
    create_operational_task(
        title=f"Review onboarding: {onboarding.organisation.legal_name}",
        task_type="onboarding_review",
        organisation=onboarding.organisation,
        description="Regulator review queue",
        priority="high",
        related_entity_type="organisation_onboarding",
        related_entity_id=onboarding.id,
        created_by=actor,
    )


def on_onboarding_approved(*, onboarding, actor, notes: str = "") -> None:
    notify_organisation_admins(
        organisation=onboarding.organisation,
        title="Organisation approved",
        body=notes or "Your organisation has been approved by the regulator.",
        severity=SEVERITY_SUCCESS,
        notification_type=NOTIFICATION_TYPE_APPROVAL,
        send_email=True,
        created_by=actor,
    )
    record_regulator_action(
        action_type=RegulatorOperationalHistory.ACTION_APPROVAL,
        summary=f"Approved {onboarding.organisation.legal_name}. {notes}".strip(),
        actor=actor,
        organisation=onboarding.organisation,
        entity_type="organisation_onboarding",
        entity_id=onboarding.id,
    )


def on_onboarding_rejected(*, onboarding, actor, reason: str) -> None:
    notify_organisation_admins(
        organisation=onboarding.organisation,
        title="Organisation application rejected",
        body=reason,
        severity=SEVERITY_WARNING,
        notification_type=NOTIFICATION_TYPE_APPROVAL,
        send_email=True,
        created_by=actor,
    )
    record_regulator_action(
        action_type=RegulatorOperationalHistory.ACTION_REJECTION,
        summary=f"Rejected {onboarding.organisation.legal_name}: {reason}",
        actor=actor,
        organisation=onboarding.organisation,
        entity_type="organisation_onboarding",
        entity_id=onboarding.id,
    )


def on_organisation_suspended(*, org, actor, reason: str) -> None:
    record_regulator_action(
        action_type=RegulatorOperationalHistory.ACTION_SUSPENSION,
        summary=f"Suspended {org.legal_name}: {reason}",
        actor=actor,
        organisation=org,
    )
    notify_organisation_admins(
        organisation=org,
        title="Organisation suspended",
        body=reason,
        severity=SEVERITY_WARNING,
        notification_type=NOTIFICATION_TYPE_APPROVAL,
        created_by=actor,
    )
