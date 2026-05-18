"""Phase 15 — in-app and email notification delivery."""
from __future__ import annotations

import uuid
from typing import Iterable

from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.notifications.constants import (
    CHANNEL_EMAIL,
    CHANNEL_IN_APP,
    NOTIFICATION_TYPE_ONBOARDING,
    SEVERITY_INFO,
)
from apps.notifications.email_service import send_platform_email
from apps.notifications.models import Notification
from apps.tenancy.models import OrganisationMembership

User = get_user_model()


def deliver_notification(
    *,
    recipient,
    title: str,
    body: str = "",
    severity: str = SEVERITY_INFO,
    notification_type: str = "",
    organisation=None,
    channel: str = CHANNEL_IN_APP,
    send_email: bool = False,
    related_entity_type: str = "",
    related_entity_id: uuid.UUID | None = None,
    created_by=None,
) -> Notification:
    """Create in-app notification and optionally queue email."""
    notification = Notification.objects.create(
        recipient=recipient,
        title=title,
        body=body,
        channel=channel,
        severity=severity,
        notification_type=notification_type,
        organisation=organisation,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
        created_by=created_by,
    )

    if send_email and getattr(recipient, "email", None):
        ref = send_platform_email(
            subject=title,
            message=body or title,
            recipient_list=[recipient.email],
        )
        notification.email_status = "queued" if ref.startswith("celery:") else "sent"
        notification.email_sent_at = timezone.now()
        notification.save(update_fields=["email_status", "email_sent_at", "updated_at"])
    return notification


def notify_organisation_admins(
    *,
    organisation,
    title: str,
    body: str = "",
    severity: str = SEVERITY_INFO,
    notification_type: str = NOTIFICATION_TYPE_ONBOARDING,
    send_email: bool = False,
    created_by=None,
) -> list[Notification]:
    """Notify active organisation members (admins and staff)."""
    user_ids = OrganisationMembership.objects.filter(
        organisation=organisation,
        membership_status=OrganisationMembership.STATUS_ACTIVE,
    ).values_list("user_id", flat=True)
    sent = []
    for user in User.objects.filter(id__in=user_ids, is_active=True):
        sent.append(
            deliver_notification(
                recipient=user,
                title=title,
                body=body,
                severity=severity,
                notification_type=notification_type,
                organisation=organisation,
                send_email=send_email,
                created_by=created_by,
            )
        )
    return sent


def render_invitation_email(*, organisation_name: str, role_name: str, accept_url: str) -> tuple[str, str]:
    subject = f"NPTTE invitation — {organisation_name}"
    body = (
        f"You have been invited to join {organisation_name} on NPTTE PharmaNG as {role_name}.\n\n"
        f"Accept your invitation: {accept_url}\n\n"
        "This link expires in 7 days."
    )
    return subject, body
