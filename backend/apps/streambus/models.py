"""Phase 17 — event bus audit, subscriptions, telemetry, deferred processing."""
from django.conf import settings
from django.db import models

from apps.core.models import NPTTEBaseModel
from apps.organisations.models import Organisation


class EventBusSubscription(NPTTEBaseModel):
    """Consumer subscription for operational events."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="event_bus_subscriptions",
    )
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="event_bus_subscriptions",
    )
    subscribed_event_types = models.JSONField(default=list, blank=True)
    channel = models.CharField(max_length=32, default="sse", db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]


class EventLifecycleLog(NPTTEBaseModel):
    """Append-only event delivery and replay audit trail."""

    event_id = models.CharField(max_length=64, db_index=True)
    correlation_id = models.UUIDField(db_index=True)
    event_type = models.CharField(max_length=64, db_index=True)
    category = models.CharField(max_length=32, db_index=True)
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="event_lifecycle_logs",
    )
    severity = models.CharField(max_length=16, default="INFO", db_index=True)
    lifecycle_state = models.CharField(max_length=32, db_index=True)
    delivery_channel = models.CharField(max_length=32, db_index=True)
    retry_count = models.PositiveSmallIntegerField(default=0)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    sequence_number = models.BigIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organisation", "-created_at"]),
            models.Index(fields=["correlation_id"]),
        ]


class OperationalTelemetrySnapshot(NPTTEBaseModel):
    """Aggregated throughput and operational velocity metrics."""

    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="telemetry_snapshots",
    )
    window_seconds = models.PositiveIntegerField(default=3600)
    scan_throughput = models.PositiveIntegerField(default=0)
    event_throughput = models.PositiveIntegerField(default=0)
    verification_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    suspicious_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    onboarding_velocity = models.PositiveIntegerField(default=0)
    recall_execution_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    metrics = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]


class DeferredProcessingTask(NPTTEBaseModel):
    """Retry-ready async task queue (inline when Celery absent)."""

    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"

    task_name = models.CharField(max_length=128, db_index=True)
    payload = models.JSONField(default=dict)
    task_status = models.CharField(max_length=32, default=STATUS_PENDING, db_index=True)
    retry_count = models.PositiveSmallIntegerField(default=0)
    max_retries = models.PositiveSmallIntegerField(default=3)
    scheduled_at = models.DateTimeField(null=True, blank=True, db_index=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ["scheduled_at", "-created_at"]


class EventEscalation(NPTTEBaseModel):
    """Realtime alert escalation records."""

    event_id = models.CharField(max_length=64, db_index=True)
    correlation_id = models.UUIDField(db_index=True)
    escalation_type = models.CharField(max_length=64, db_index=True)
    severity = models.CharField(max_length=16, db_index=True)
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="event_escalations",
    )
    summary = models.TextField()
    is_acknowledged = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["-created_at"]
