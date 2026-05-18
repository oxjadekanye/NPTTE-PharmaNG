"""Phase 15 — workflow timelines, regulator history, documents, tasks, activity feeds."""
from django.conf import settings
from django.db import models

from apps.core.models import NPTTEBaseModel
from apps.organisations.models import Organisation


class WorkflowTimelineEntry(NPTTEBaseModel):
    """Persistent operational workflow events (onboarding, recalls, approvals)."""

    WORKFLOW_RECALL = "recall"
    WORKFLOW_ONBOARDING = "onboarding"
    WORKFLOW_INVITATION = "invitation"
    WORKFLOW_RECALL = "recall"
    WORKFLOW_APPROVAL = "approval"
    WORKFLOW_INSPECTION = "inspection"
    WORKFLOW_ORGANISATION = "organisation"

    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="workflow_timeline_entries",
    )
    workflow_type = models.CharField(max_length=64, db_index=True)
    entity_type = models.CharField(max_length=128, blank=True, db_index=True)
    entity_id = models.UUIDField(null=True, blank=True, db_index=True)
    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="workflow_actions",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organisation", "workflow_type", "-created_at"]),
        ]


class RegulatorOperationalHistory(NPTTEBaseModel):
    """Append-only regulator operational audit trail."""

    ACTION_APPROVAL = "organisation_approval"
    ACTION_REJECTION = "organisation_rejection"
    ACTION_SUSPENSION = "organisation_suspension"
    ACTION_REACTIVATION = "organisation_reactivation"
    ACTION_RECALL = "recall"
    ACTION_INVESTIGATION = "investigation"
    ACTION_ONBOARDING_REVIEW = "onboarding_review"
    ACTION_INVITATION_REVOKE = "invitation_revocation"
    ACTION_ESCALATION = "escalation"

    action_type = models.CharField(max_length=64, db_index=True)
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="regulator_history",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="regulator_operational_actions",
    )
    summary = models.TextField()
    entity_type = models.CharField(max_length=128, blank=True)
    entity_id = models.UUIDField(null=True, blank=True)
    is_immutable = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Regulator operational histories"


class OperationalDocument(NPTTEBaseModel):
    """Organisation-owned compliance and operational documents."""

    DOC_CAC = "cac_certificate"
    DOC_LICENCE = "licence"
    DOC_INSPECTION = "inspection_evidence"
    DOC_COMPLIANCE = "compliance"
    DOC_RECALL = "recall"
    DOC_BATCH_CERT = "batch_certificate"

    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name="operational_documents",
    )
    document_type = models.CharField(max_length=64, db_index=True)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="operational_documents/%Y/%m/", blank=True)
    storage_key = models.CharField(max_length=512, blank=True)
    original_filename = models.CharField(max_length=255, blank=True)
    file_size = models.PositiveIntegerField(default=0)
    content_type = models.CharField(max_length=128, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_operational_documents",
    )

    class Meta:
        ordering = ["-created_at"]


class OperationalTask(NPTTEBaseModel):
    """Lightweight operational task queue."""

    STATUS_OPEN = "open"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"

    ESC_NONE = "none"
    ESC_ESCALATED = "escalated"

    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="operational_tasks",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_operational_tasks",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    task_type = models.CharField(max_length=64, db_index=True)
    priority = models.CharField(max_length=16, default="normal", db_index=True)
    due_at = models.DateTimeField(null=True, blank=True, db_index=True)
    escalation_status = models.CharField(max_length=32, default=ESC_NONE, db_index=True)
    task_status = models.CharField(max_length=32, default=STATUS_OPEN, db_index=True)
    related_entity_type = models.CharField(max_length=128, blank=True)
    related_entity_id = models.UUIDField(null=True, blank=True)

    class Meta:
        ordering = ["due_at", "-created_at"]


class ActivityFeedEntry(NPTTEBaseModel):
    """Persistent operational activity feed."""

    VIS_ORGANISATION = "organisation"
    VIS_REGULATOR = "regulator"
    VIS_NATIONAL = "national"

    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="activity_feed_entries",
    )
    visibility = models.CharField(max_length=32, default=VIS_ORGANISATION, db_index=True)
    feed_type = models.CharField(max_length=64, db_index=True)
    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True)
    severity = models.CharField(max_length=16, default="INFO", db_index=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activity_feed_actions",
    )
    entity_type = models.CharField(max_length=128, blank=True)
    entity_id = models.UUIDField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organisation", "-created_at"]),
            models.Index(fields=["visibility", "-created_at"]),
        ]
