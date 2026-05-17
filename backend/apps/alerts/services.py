"""National alert services."""
from __future__ import annotations

from decimal import Decimal

from apps.alerts.models import NationalAlert, NationalAlertEscalation
from apps.core.constants import AlertSeverity


def create_national_alert(
    *,
    alert_type: str,
    title: str,
    description: str = "",
    severity: str = AlertSeverity.WARNING,
    risk_score: Decimal = Decimal("50"),
    organisation=None,
    product=None,
    state: str = "",
    evidence_payload: dict | None = None,
) -> NationalAlert:
    return NationalAlert.objects.create(
        alert_type=alert_type,
        title=title,
        description=description,
        severity=severity,
        risk_score=risk_score,
        organisation=organisation,
        product=product,
        state=state,
        evidence_payload=evidence_payload or {},
    )


def escalate_alert(*, alert: NationalAlert, escalated_to: str, notes: str = "") -> NationalAlertEscalation:
    escalation = NationalAlertEscalation.objects.create(
        alert=alert,
        escalated_to=escalated_to,
        notes=notes,
    )
    alert.escalation_level += 1
    alert.save(update_fields=["escalation_level", "updated_at"])
    return escalation
