"""Phase 18 — national risk intelligence models."""
from django.db import models

from apps.core.models import NPTTEBaseModel
from apps.organisations.models import Organisation
from apps.products.models import Product


class NationalRiskSnapshot(NPTTEBaseModel):
    national_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, db_index=True)
    status = models.CharField(max_length=16, default="green", db_index=True)
    confidence = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    reasons = models.JSONField(default=list, blank=True)
    recommended_actions = models.JSONField(default=list, blank=True)
    metrics = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]


class OrganisationRiskProfile(NPTTEBaseModel):
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name="intelligence_risk_profiles",
    )
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0, db_index=True)
    status = models.CharField(max_length=16, default="green", db_index=True)
    confidence = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    integrity_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    reasons = models.JSONField(default=list, blank=True)
    recommended_actions = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["-score"]
        indexes = [models.Index(fields=["organisation", "-created_at"])]


class ProductRiskProfile(NPTTEBaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="intelligence_risk_profiles")
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0, db_index=True)
    status = models.CharField(max_length=16, default="green", db_index=True)
    confidence = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    counterfeit_probability = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    reasons = models.JSONField(default=list, blank=True)
    recommended_actions = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["-score"]


class RegionalRiskProfile(NPTTEBaseModel):
    region_state = models.CharField(max_length=128, db_index=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0, db_index=True)
    status = models.CharField(max_length=16, default="green", db_index=True)
    confidence = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    scan_density = models.PositiveIntegerField(default=0)
    suspicious_count = models.PositiveIntegerField(default=0)
    reasons = models.JSONField(default=list, blank=True)
    recommended_actions = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["-score"]


class IntelligenceSignal(NPTTEBaseModel):
    SIGNAL_SUSPICIOUS_SCAN = "suspicious_scan"
    SIGNAL_DUPLICATE = "duplicate_scan"
    SIGNAL_RECALL_DELAY = "recall_delay"
    SIGNAL_CUSTODY_GAP = "custody_gap"
    SIGNAL_CLUSTER = "cluster_anomaly"

    signal_type = models.CharField(max_length=64, db_index=True)
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="intelligence_signals",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="intelligence_signals",
    )
    region_state = models.CharField(max_length=128, blank=True, db_index=True)
    severity = models.CharField(max_length=16, default="medium", db_index=True)
    confidence = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True)
    evidence = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]


class CounterfeitCluster(NPTTEBaseModel):
    cluster_code = models.CharField(max_length=32, unique=True, db_index=True)
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="counterfeit_clusters",
    )
    region_state = models.CharField(max_length=128, blank=True, db_index=True)
    scan_count = models.PositiveIntegerField(default=0)
    suspicious_count = models.PositiveIntegerField(default=0)
    confidence = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    status = models.CharField(max_length=16, default="open", db_index=True)
    serial_numbers = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["-suspicious_count"]


class IntelligenceNarrative(NPTTEBaseModel):
    NARRATIVE_EXECUTIVE = "executive"
    NARRATIVE_INCIDENT = "incident"
    NARRATIVE_REGIONAL = "regional"
    NARRATIVE_RECALL = "recall"
    NARRATIVE_ENFORCEMENT = "enforcement"
    NARRATIVE_MINISTERIAL = "ministerial"

    narrative_type = models.CharField(max_length=64, db_index=True)
    title = models.CharField(max_length=255)
    body = models.TextField()
    context = models.JSONField(default=dict, blank=True)
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="intelligence_narratives",
    )

    class Meta:
        ordering = ["-created_at"]
