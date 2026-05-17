from django.db import models

from apps.core.constants import RiskLevel
from apps.core.models import NPTTEBaseModel
from apps.organisations.models import Organisation


class AIRiskAssessment(NPTTEBaseModel):
    """AI/ML risk assessment record (rule-based until models are deployed)."""

    assessment_type = models.CharField(max_length=64, db_index=True)
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_assessments",
    )
    risk_level = models.CharField(max_length=16, choices=RiskLevel.CHOICES, db_index=True)
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    model_version = models.CharField(max_length=32, default="rules-v1")
    input_features = models.JSONField(default=dict, blank=True)
    output_explanation = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["assessment_type", "risk_level", "created_at"]),
        ]
