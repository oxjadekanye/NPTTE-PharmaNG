"""
Regulatory alert and inspection foundation models.
"""
from django.db import models

from apps.core.constants import AlertSeverity
from apps.core.models import NPTTEBaseModel
from apps.organisations.models import Organisation


class RegulatoryAlert(NPTTEBaseModel):
    """
    Regulator-facing alert for supply chain or compliance anomalies.

    Linked organisations and resolution workflows will expand in later phases.
    """

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    severity = models.CharField(
        max_length=16,
        choices=AlertSeverity.CHOICES,
        default=AlertSeverity.INFO,
        db_index=True,
    )
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="regulatory_alerts",
    )
    alert_type = models.CharField(max_length=64, db_index=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Regulatory alert"
        verbose_name_plural = "Regulatory alerts"

    def __str__(self):
        return self.title
