"""Phase 18 — enforcement case management models."""
from django.conf import settings
from django.db import models

from apps.core.models import NPTTEBaseModel
from apps.organisations.models import Organisation


class EnforcementCase(NPTTEBaseModel):
    STATUS_OPEN = "open"
    STATUS_INVESTIGATING = "investigating"
    STATUS_ESCALATED = "escalated"
    STATUS_ENFORCEMENT_PENDING = "enforcement_pending"
    STATUS_RESOLVED = "resolved"
    STATUS_CLOSED = "closed"

    SEV_LOW = "low"
    SEV_MEDIUM = "medium"
    SEV_HIGH = "high"
    SEV_CRITICAL = "critical"

    case_reference = models.CharField(max_length=32, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True)
    case_status = models.CharField(max_length=32, default=STATUS_OPEN, db_index=True)
    severity = models.CharField(max_length=16, default=SEV_MEDIUM, db_index=True)
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="enforcement_cases",
    )
    intelligence_signal_id = models.UUIDField(null=True, blank=True, db_index=True)
    assigned_regulator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_enforcement_cases",
    )

    class Meta:
        ordering = ["-created_at"]


class EnforcementRecommendation(NPTTEBaseModel):
    REC_INSPECTION = "recommend_inspection"
    REC_RECALL_ESCALATION = "recommend_recall_escalation"
    REC_CUSTOMS_HOLD = "recommend_customs_hold"
    REC_PHARMACY_REVIEW = "recommend_pharmacy_review"
    REC_DISTRIBUTOR_INVESTIGATION = "recommend_distributor_investigation"
    REC_SUSPENSION = "recommend_suspension"

    STATUS_PENDING = "pending"
    STATUS_ACCEPTED = "accepted"
    STATUS_DISMISSED = "dismissed"

    recommendation_type = models.CharField(max_length=64, db_index=True)
    title = models.CharField(max_length=255)
    rationale = models.TextField(blank=True)
    recommendation_status = models.CharField(max_length=32, default=STATUS_PENDING, db_index=True)
    severity = models.CharField(max_length=16, default="medium", db_index=True)
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="enforcement_recommendations",
    )
    case = models.ForeignKey(
        EnforcementCase,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recommendations",
    )
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        ordering = ["-created_at"]


class EnforcementAction(NPTTEBaseModel):
    case = models.ForeignKey(EnforcementCase, on_delete=models.CASCADE, related_name="actions")
    action_type = models.CharField(max_length=64, db_index=True)
    notes = models.TextField(blank=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="enforcement_actions",
    )

    class Meta:
        ordering = ["-created_at"]


class InvestigationAssignment(NPTTEBaseModel):
    case = models.ForeignKey(EnforcementCase, on_delete=models.CASCADE, related_name="assignments")
    investigator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="investigation_assignments",
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-assigned_at"]


class EnforcementTimelineEntry(NPTTEBaseModel):
    case = models.ForeignKey(
        EnforcementCase,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="timeline_entries",
    )
    entry_type = models.CharField(max_length=64, db_index=True)
    summary = models.TextField()
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="enforcement_timeline_entries",
    )

    class Meta:
        ordering = ["-created_at"]
