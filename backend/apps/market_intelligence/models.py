from django.db import models

from apps.core.models import NPTTEBaseModel
from apps.organisations.models import Organisation
from apps.products.models import Product


class MedicinePriceIndex(NPTTEBaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="price_indices")
    state = models.CharField(max_length=128, db_index=True)
    reference_price = models.DecimalField(max_digits=12, decimal_places=2)
    observed_price = models.DecimalField(max_digits=12, decimal_places=2)
    recorded_at = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ["-recorded_at"]
        indexes = [models.Index(fields=["product", "state", "recorded_at"])]


class RegionalPriceVariance(NPTTEBaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="price_variances")
    state = models.CharField(max_length=128, db_index=True)
    variance_percent = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    national_median = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ["-variance_percent"]


class MarketShortageSignal(NPTTEBaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="shortage_signals")
    state = models.CharField(max_length=128, db_index=True)
    pressure_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, db_index=True)
    detected_at = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ["-pressure_score"]


class PriceManipulationAlert(NPTTEBaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="price_alerts")
    organisation = models.ForeignKey(
        Organisation, on_delete=models.SET_NULL, null=True, related_name="price_manipulation_alerts"
    )
    spike_percent = models.DecimalField(max_digits=6, decimal_places=2)
    is_confirmed = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["-created_at"]


class SubsidyTrackingRecord(NPTTEBaseModel):
    """NHIA subsidy intelligence readiness."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="subsidy_records")
    nhia_code = models.CharField(max_length=64, blank=True, db_index=True)
    subsidised_price = models.DecimalField(max_digits=12, decimal_places=2)
    coverage_states = models.JSONField(default=list, blank=True)
    effective_from = models.DateField(db_index=True)

    class Meta:
        ordering = ["-effective_from"]
