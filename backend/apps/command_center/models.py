from django.db import models

from apps.core.constants import IncidentSeverity, IncidentStatus, RiskLevel
from apps.core.models import NPTTEBaseModel
from apps.organisations.models import Organisation
from apps.products.models import Product


class NationalIncident(NPTTEBaseModel):
    incident_code = models.CharField(max_length=64, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    severity = models.CharField(max_length=16, choices=IncidentSeverity.CHOICES, db_index=True)
    status = models.CharField(
        max_length=32, choices=IncidentStatus.CHOICES, default=IncidentStatus.OPEN, db_index=True
    )
    assigned_investigator = models.CharField(max_length=255, blank=True, db_index=True)
    escalation_level = models.PositiveSmallIntegerField(default=1, db_index=True)
    workflow_state = models.CharField(max_length=64, default="open", db_index=True)
    evidence_lifecycle = models.JSONField(default=list, blank=True)
    affected_states = models.JSONField(default=list, blank=True)
    organisation = models.ForeignKey(
        Organisation, on_delete=models.SET_NULL, null=True, blank=True, related_name="incidents"
    )
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, blank=True, related_name="incidents"
    )
    threat_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["status", "severity", "created_at"])]


class RegionalHealthSignal(NPTTEBaseModel):
    state = models.CharField(max_length=128, db_index=True)
    signal_type = models.CharField(max_length=64, db_index=True)
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, db_index=True)
    evidence = models.JSONField(default=dict, blank=True)
    recorded_at = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ["-recorded_at"]
        indexes = [models.Index(fields=["state", "signal_type", "recorded_at"])]


class SupplyChainDisruption(NPTTEBaseModel):
    disruption_type = models.CharField(max_length=64, db_index=True)
    origin_organisation = models.ForeignKey(
        Organisation, on_delete=models.SET_NULL, null=True, related_name="disruptions_origin"
    )
    destination_organisation = models.ForeignKey(
        Organisation, on_delete=models.SET_NULL, null=True, related_name="disruptions_destination"
    )
    impact_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_active_disruption = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]


class EmergencyIntervention(NPTTEBaseModel):
    intervention_code = models.CharField(max_length=64, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    target_states = models.JSONField(default=list, blank=True)
    priority_level = models.CharField(max_length=16, choices=RiskLevel.CHOICES, db_index=True)
    activated_at = models.DateTimeField(null=True, blank=True, db_index=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]


class RegulatoryAction(NPTTEBaseModel):
    action_type = models.CharField(max_length=64, db_index=True)
    target_organisation = models.ForeignKey(
        Organisation, on_delete=models.PROTECT, related_name="regulatory_actions"
    )
    reference_number = models.CharField(max_length=128, db_index=True)
    is_immutable = models.BooleanField(default=True)
    action_payload = models.JSONField(default=dict, blank=True)
    executed_at = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ["-executed_at"]


class NationalThreatAssessment(NPTTEBaseModel):
    assessment_period = models.CharField(max_length=32, db_index=True)
    national_risk_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, db_index=True)
    counterfeit_risk = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    shortage_risk = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    diversion_risk = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    regional_breakdown = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
