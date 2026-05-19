from django.db import models

from apps.core.constants import AlertSeverity, RiskLevel
from apps.core.models import NPTTEBaseModel
from apps.organisations.models import Organisation
from apps.products.models import Product


class NationalAlert(NPTTEBaseModel):
    """Cross-cutting national alert for regulators and operators."""

    alert_type = models.CharField(max_length=64, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    severity = models.CharField(
        max_length=16,
        choices=AlertSeverity.CHOICES,
        default=AlertSeverity.INFO,
        db_index=True,
    )
    risk_level = models.CharField(
        max_length=16,
        choices=RiskLevel.CHOICES,
        default=RiskLevel.LOW,
        db_index=True,
    )
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="national_alerts",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="national_alerts",
    )
    state = models.CharField(max_length=128, blank=True, db_index=True)
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, db_index=True)
    evidence_payload = models.JSONField(default=dict, blank=True)
    escalation_level = models.PositiveIntegerField(default=0)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["alert_type", "severity", "created_at"]),
            models.Index(fields=["state", "risk_level"]),
            models.Index(fields=["risk_score", "created_at"]),
            # Phase 20A.4 — kept in sync with 0003_phase20a4_alert_perf_indexes
            models.Index(fields=["resolved_at", "created_at"], name="alert_resolved_created_idx"),
            models.Index(fields=["severity", "resolved_at"], name="alert_sev_resolved_idx"),
        ]


class NationalAlertEscalation(NPTTEBaseModel):
    """Escalation workflow for national alerts."""

    alert = models.ForeignKey(
        NationalAlert,
        on_delete=models.CASCADE,
        related_name="escalations",
    )
    escalated_to = models.CharField(max_length=128, db_index=True)
    notes = models.TextField(blank=True)
    escalated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-escalated_at"]
        verbose_name = "Alert escalation"
        verbose_name_plural = "Alert escalations"
