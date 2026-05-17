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
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["alert_type", "severity", "created_at"]),
            models.Index(fields=["state", "risk_level"]),
        ]
