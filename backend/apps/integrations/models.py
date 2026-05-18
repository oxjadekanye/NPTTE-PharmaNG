"""Phase 16 — integration models for providers, webhooks, exports, and analytics."""
from django.conf import settings
from django.db import models

from apps.core.models import NPTTEBaseModel
from apps.organisations.models import Organisation


class ProviderHealthStatus(NPTTEBaseModel):
    """Health snapshot for email, SMS, storage, and webhook providers."""

    PROVIDER_EMAIL = "email"
    PROVIDER_SMS = "sms"
    PROVIDER_PUSH = "push"
    PROVIDER_STORAGE = "storage"
    PROVIDER_WEBHOOK = "webhook"

    STATUS_HEALTHY = "healthy"
    STATUS_DEGRADED = "degraded"
    STATUS_UNAVAILABLE = "unavailable"

    provider_type = models.CharField(max_length=32, db_index=True)
    provider_name = models.CharField(max_length=64, db_index=True)
    status = models.CharField(max_length=32, default=STATUS_HEALTHY, db_index=True)
    last_checked_at = models.DateTimeField(auto_now=True)
    message = models.TextField(blank=True)

    class Meta:
        ordering = ["provider_type", "provider_name"]
        unique_together = [("provider_type", "provider_name")]


class EmailDeliveryLog(NPTTEBaseModel):
    recipient = models.CharField(max_length=255, db_index=True)
    subject = models.CharField(max_length=255)
    provider_name = models.CharField(max_length=64, default="console", db_index=True)
    delivery_status = models.CharField(max_length=32, default="pending", db_index=True)
    retry_count = models.PositiveSmallIntegerField(default=0)
    error_message = models.TextField(blank=True)
    organisation = models.ForeignKey(
        Organisation, on_delete=models.SET_NULL, null=True, blank=True, related_name="email_delivery_logs"
    )

    class Meta:
        ordering = ["-created_at"]


class SMSDeliveryLog(NPTTEBaseModel):
    phone_number = models.CharField(max_length=32, db_index=True)
    message_body = models.TextField()
    provider_name = models.CharField(max_length=64, default="mock", db_index=True)
    delivery_status = models.CharField(max_length=32, default="pending", db_index=True)
    retry_count = models.PositiveSmallIntegerField(default=0)
    notification_type = models.CharField(max_length=64, blank=True, db_index=True)
    organisation = models.ForeignKey(
        Organisation, on_delete=models.SET_NULL, null=True, blank=True, related_name="sms_delivery_logs"
    )

    class Meta:
        ordering = ["-created_at"]


class PushDeviceRegistration(NPTTEBaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="push_device_registrations",
    )
    platform = models.CharField(max_length=32, default="web", db_index=True)
    endpoint = models.TextField(blank=True)
    subscription_keys = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]


class WebhookSubscription(NPTTEBaseModel):
    EVENT_RECALL_CREATED = "recall_created"
    EVENT_BATCH_APPROVED = "batch_approved"
    EVENT_SUSPICIOUS_SCAN = "suspicious_scan"
    EVENT_ONBOARDING_APPROVED = "onboarding_approved"
    EVENT_ORGANISATION_SUSPENDED = "organisation_suspended"

    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="webhook_subscriptions",
    )
    target_url = models.URLField(max_length=512)
    secret = models.CharField(max_length=128, blank=True)
    subscribed_events = models.JSONField(default=list, blank=True)
    is_active_subscription = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]


class WebhookDeliveryLog(NPTTEBaseModel):
    subscription = models.ForeignKey(
        WebhookSubscription,
        on_delete=models.CASCADE,
        related_name="delivery_logs",
    )
    event_type = models.CharField(max_length=64, db_index=True)
    payload = models.JSONField(default=dict)
    delivery_status = models.CharField(max_length=32, default="pending", db_index=True)
    http_status = models.PositiveSmallIntegerField(null=True, blank=True)
    retry_count = models.PositiveSmallIntegerField(default=0)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]


class ExternalIntegrationConnector(NPTTEBaseModel):
    CONNECTOR_PHARMACY = "pharmacy"
    CONNECTOR_ERP = "erp"
    CONNECTOR_WAREHOUSE = "warehouse"
    CONNECTOR_CUSTOMS = "customs"
    CONNECTOR_MANUFACTURER = "manufacturer"

    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name="external_connectors",
    )
    connector_type = models.CharField(max_length=64, db_index=True)
    connector_name = models.CharField(max_length=128)
    connection_status = models.CharField(max_length=32, default="configured", db_index=True)
    endpoint_url = models.URLField(max_length=512, blank=True)

    class Meta:
        ordering = ["connector_type", "connector_name"]


class AnalyticsSnapshot(NPTTEBaseModel):
    metric_type = models.CharField(max_length=64, db_index=True)
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="analytics_snapshots",
    )
    period_start = models.DateTimeField(db_index=True)
    period_end = models.DateTimeField(db_index=True)
    metrics = models.JSONField(default=dict)

    class Meta:
        ordering = ["-period_end"]
        indexes = [models.Index(fields=["metric_type", "organisation", "-period_end"])]


class ExportJob(NPTTEBaseModel):
    EXPORT_CSV = "csv"
    EXPORT_PDF = "pdf"

    REPORT_AUDIT = "audit"
    REPORT_RECALL = "recall"
    REPORT_COMPLIANCE = "compliance"
    REPORT_TRACEABILITY = "traceability"

    STATUS_PENDING = "pending"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"

    export_format = models.CharField(max_length=16, db_index=True)
    report_type = models.CharField(max_length=64, db_index=True)
    job_status = models.CharField(max_length=32, default=STATUS_PENDING, db_index=True)
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="export_jobs",
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="export_jobs",
    )
    file_path = models.CharField(max_length=512, blank=True)
    storage_key = models.CharField(max_length=512, blank=True)
    row_count = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
