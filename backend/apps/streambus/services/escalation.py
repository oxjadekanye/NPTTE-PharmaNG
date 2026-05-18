"""Live alert escalation for suspicious scans, recalls, and health warnings."""
from __future__ import annotations

import uuid

from apps.integrations.webhooks.dispatcher import publish_integration_event
from apps.notifications.constants import SEVERITY_CRITICAL, SEVERITY_WARNING
from apps.notifications.services.delivery import deliver_notification, notify_organisation_admins
from apps.streambus.constants import EVT_RECALL, EVT_SCAN_SUSPICIOUS, SEV_CRITICAL, SEV_WARNING
from apps.streambus.models import EventEscalation
from apps.organisations.models import Organisation


def maybe_escalate_event(
    *,
    event_id: str,
    correlation_id: uuid.UUID,
    event_type: str,
    severity: str,
    organisation_id=None,
    payload: dict,
) -> EventEscalation | None:
    if event_type == EVT_SCAN_SUSPICIOUS or severity == SEV_CRITICAL:
        return _escalate(
            event_id=event_id,
            correlation_id=correlation_id,
            escalation_type="suspicious_scan",
            severity=SEV_CRITICAL,
            organisation_id=organisation_id,
            summary=payload.get("summary", "Suspicious scan detected"),
        )
    if event_type == EVT_RECALL:
        return _escalate(
            event_id=event_id,
            correlation_id=correlation_id,
            escalation_type="recall_urgency",
            severity=SEV_CRITICAL,
            organisation_id=organisation_id,
            summary=payload.get("summary", "Recall propagation event"),
        )
    if severity == SEV_WARNING:
        return _escalate(
            event_id=event_id,
            correlation_id=correlation_id,
            escalation_type="operational_warning",
            severity=SEV_WARNING,
            organisation_id=organisation_id,
            summary=payload.get("summary", "Operational warning"),
        )
    return None


def _escalate(
    *,
    event_id: str,
    correlation_id: uuid.UUID,
    escalation_type: str,
    severity: str,
    organisation_id,
    summary: str,
) -> EventEscalation:
    org = Organisation.objects.filter(pk=organisation_id).first() if organisation_id else None
    row = EventEscalation.objects.create(
        event_id=event_id,
        correlation_id=correlation_id,
        escalation_type=escalation_type,
        severity=severity,
        organisation=org,
        summary=summary,
    )
    if org:
        notify_organisation_admins(
            organisation=org,
            title=f"Escalation: {escalation_type}",
            body=summary,
            severity=SEVERITY_CRITICAL if severity == SEV_CRITICAL else SEVERITY_WARNING,
        )
    publish_integration_event(
        event_type="suspicious_scan" if "suspicious" in escalation_type else "recall_created",
        payload={"event_id": event_id, "summary": summary},
        organisation=org,
    )
    return row
