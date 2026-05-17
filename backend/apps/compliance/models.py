from django.db import models

from apps.core.models import NPTTEBaseModel
from apps.organisations.models import Organisation


class ComplianceRecord(NPTTEBaseModel):
    """Organisation compliance status for national enforcement."""

    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name="compliance_records",
    )
    regulator_code = models.CharField(max_length=32, db_index=True)
    compliance_type = models.CharField(max_length=64, db_index=True)
    is_compliant = models.BooleanField(default=True, db_index=True)
    assessed_at = models.DateTimeField(db_index=True)
    next_review_at = models.DateTimeField(null=True, blank=True)
    findings = models.TextField(blank=True)

    class Meta:
        ordering = ["-assessed_at"]
        indexes = [
            models.Index(fields=["organisation", "regulator_code", "is_compliant"]),
        ]
