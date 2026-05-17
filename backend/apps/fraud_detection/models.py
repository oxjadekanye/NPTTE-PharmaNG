from django.db import models

from apps.core.constants import RiskLevel
from apps.core.models import NPTTEBaseModel
from apps.organisations.models import Organisation
from apps.traceability.models import SupplyChainTransaction


class FraudRiskFlag(NPTTEBaseModel):
    """Suspicious activity flag linked to organisations or transactions."""

    flag_type = models.CharField(max_length=64, db_index=True)
    risk_level = models.CharField(
        max_length=16,
        choices=RiskLevel.CHOICES,
        default=RiskLevel.MEDIUM,
        db_index=True,
    )
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, db_index=True)
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fraud_flags",
    )
    supply_chain_transaction = models.ForeignKey(
        SupplyChainTransaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fraud_flags",
    )
    description = models.TextField(blank=True)
    is_resolved = models.BooleanField(default=False, db_index=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-risk_score", "-created_at"]
        indexes = [
            models.Index(fields=["flag_type", "risk_level", "is_resolved"]),
        ]
