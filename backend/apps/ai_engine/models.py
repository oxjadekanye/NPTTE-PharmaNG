from django.db import models

from apps.core.constants import RiskLevel
from apps.core.models import NPTTEBaseModel
from apps.organisations.models import Organisation
from apps.products.models import Product


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


class AIRiskSignal(NPTTEBaseModel):
    signal_type = models.CharField(max_length=64, db_index=True)
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_risk_signals",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_risk_signals",
    )
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0, db_index=True)
    evidence = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]


class DemandForecast(NPTTEBaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="demand_forecasts")
    region_state = models.CharField(max_length=128, db_index=True)
    forecast_date = models.DateField(db_index=True)
    predicted_demand = models.PositiveIntegerField(default=0)
    confidence = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    model_version = models.CharField(max_length=32, default="rules-v1")

    class Meta:
        ordering = ["-forecast_date"]
        indexes = [models.Index(fields=["region_state", "forecast_date"])]


class InventoryPrediction(NPTTEBaseModel):
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name="inventory_predictions",
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="inventory_predictions")
    predicted_stock_days_remaining = models.PositiveIntegerField(default=0)
    shortage_probability = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    model_version = models.CharField(max_length=32, default="rules-v1")

    class Meta:
        ordering = ["-created_at"]


class CounterfeitRiskAssessment(NPTTEBaseModel):
    serial_number = models.CharField(max_length=128, db_index=True)
    probability = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    risk_level = models.CharField(max_length=16, choices=RiskLevel.CHOICES, db_index=True)
    factors = models.JSONField(default=dict, blank=True)
    model_version = models.CharField(max_length=32, default="rules-v1")

    class Meta:
        ordering = ["-created_at"]


class OrganisationRiskScore(NPTTEBaseModel):
    organisation = models.OneToOneField(
        Organisation,
        on_delete=models.CASCADE,
        related_name="risk_score_profile",
    )
    overall_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, db_index=True)
    counterfeit_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    diversion_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    velocity_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    last_calculated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Organisation risk score"
        verbose_name_plural = "Organisation risk scores"


class NationalRiskSignal(NPTTEBaseModel):
    signal_type = models.CharField(max_length=64, db_index=True)
    national_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, db_index=True)
    regional_data = models.JSONField(default=dict, blank=True)
    recorded_at = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ["-recorded_at"]


class CounterfeitHeatmap(NPTTEBaseModel):
    state = models.CharField(max_length=128, db_index=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    intensity = models.DecimalField(max_digits=5, decimal_places=2, default=0, db_index=True)
    period_start = models.DateTimeField(db_index=True)
    period_end = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ["-intensity"]


class DiversionProbability(NPTTEBaseModel):
    organisation = models.ForeignKey(
        Organisation, on_delete=models.CASCADE, related_name="diversion_probabilities"
    )
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, blank=True, related_name="diversion_probabilities"
    )
    probability = models.DecimalField(max_digits=5, decimal_places=2, default=0, db_index=True)
    factors = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-probability"]


class ShortageForecast(NPTTEBaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="shortage_forecasts")
    state = models.CharField(max_length=128, db_index=True)
    forecast_date = models.DateField(db_index=True)
    shortage_probability = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    model_version = models.CharField(max_length=32, default="rules-v1")

    class Meta:
        ordering = ["-forecast_date"]


class MedicineMovementPattern(NPTTEBaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="movement_patterns")
    origin_state = models.CharField(max_length=128, db_index=True)
    destination_state = models.CharField(max_length=128, db_index=True)
    movement_volume = models.PositiveIntegerField(default=0)
    anomaly_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, db_index=True)
    period_start = models.DateTimeField(db_index=True)
    period_end = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ["-anomaly_score"]
