"""National prescription intelligence services."""
from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from apps.core.constants import AlertCategory, AlertSeverity
from apps.prescriptions.models import DispensingRecord, Prescription, RefillAuthorization


def calculate_prescription_risk(*, prescription: Prescription) -> Decimal:
    """Heuristic prescription abuse and diversion risk scoring."""
    score = Decimal("0")
    if prescription.is_controlled_substance:
        score += Decimal("25")

    refill = RefillAuthorization.objects.filter(prescription=prescription).first()
    if refill and refill.authorized_refills > 0:
        ratio = refill.refills_used / max(refill.authorized_refills, 1)
        if ratio > 0.8:
            score += Decimal("30")

    recent_dispenses = DispensingRecord.objects.filter(
        prescription__patient=prescription.patient,
        dispensed_at__gte=timezone.now() - timedelta(days=30),
    ).count()
    if recent_dispenses > 10:
        score += Decimal("35")

    duplicate = DispensingRecord.objects.filter(
        prescription=prescription,
        dispensed_at__gte=timezone.now() - timedelta(hours=48),
    ).count()
    if duplicate > 1:
        score += Decimal("40")

    prescription.risk_score = min(score, Decimal("100"))
    prescription.save(update_fields=["risk_score", "updated_at"])

    if score >= 60:
        from apps.alerts.services import create_national_alert

        create_national_alert(
            alert_type=AlertCategory.DIVERSION,
            title=f"High prescription risk: {prescription.prescription_number}",
            description="Abuse indicators detected on national prescription engine.",
            severity=AlertSeverity.WARNING if score < 80 else AlertSeverity.CRITICAL,
            risk_score=score,
            organisation=prescription.prescriber_organisation,
        )
    return prescription.risk_score
