from django.conf import settings
from django.db import models

from apps.core.models import NPTTEBaseModel
from apps.organisations.models import Organisation


class DeviceRegistration(NPTTEBaseModel):
    """Mobile, scanner, and customs device registration for sync and trust scoring."""

    device_id = models.CharField(max_length=128, unique=True, db_index=True)
    device_type = models.CharField(
        max_length=32,
        db_index=True,
        help_text="android, ios, regulator_tablet, warehouse_scanner, customs",
    )
    organisation = models.ForeignKey(
        Organisation, on_delete=models.SET_NULL, null=True, blank=True, related_name="devices"
    )
    trust_score = models.DecimalField(max_digits=5, decimal_places=2, default=50, db_index=True)
    last_sync_at = models.DateTimeField(null=True, blank=True, db_index=True)
    offline_sync_token = models.CharField(max_length=64, blank=True, db_index=True)
    app_version = models.CharField(max_length=32, blank=True)
    # Phase 22 — device trust
    fingerprint_hash = models.CharField(max_length=128, blank=True, db_index=True)
    platform = models.CharField(max_length=32, blank=True, db_index=True)
    os_version = models.CharField(max_length=64, blank=True)
    assigned_role_code = models.CharField(max_length=64, blank=True, db_index=True)
    trusted_status = models.CharField(
        max_length=16,
        default="pending",
        db_index=True,
        help_text="pending|trusted|suspended",
    )
    device_risk_level = models.CharField(
        max_length=16,
        default="low",
        db_index=True,
        help_text="low|medium|high",
    )
    is_emulator = models.BooleanField(default=False)
    is_rooted_flag = models.BooleanField(default=False)
    suspicious_device = models.BooleanField(default=False, db_index=True)
    last_heartbeat_at = models.DateTimeField(null=True, blank=True, db_index=True)
    biometric_capable = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["device_type", "trust_score"]),
            models.Index(fields=["trusted_status", "device_risk_level"]),
        ]


class OfflineScanQueue(NPTTEBaseModel):
    """Offline-first scan cache for sync when connectivity returns (Phase 10)."""

    device = models.ForeignKey(
        DeviceRegistration,
        on_delete=models.CASCADE,
        related_name="offline_scans",
    )
    raw_scan = models.CharField(max_length=512)
    scan_source = models.CharField(max_length=32, db_index=True)
    scanner_type = models.CharField(max_length=32, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    replay_nonce = models.CharField(max_length=64, blank=True, db_index=True)
    sync_status = models.CharField(max_length=32, default="pending", db_index=True)
    sync_attempts = models.PositiveSmallIntegerField(default=0)
    synced_at = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [models.Index(fields=["sync_status", "created_at"])]


class MobileFieldEvidence(NPTTEBaseModel):
    """Phase 22 — field evidence capture (photos as compact payloads)."""

    SYNC_PENDING = "pending"
    SYNC_SYNCED = "synced"
    SYNC_FAILED = "failed"

    device = models.ForeignKey(
        DeviceRegistration,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="field_evidence",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mobile_field_evidence",
    )
    evidence_type = models.CharField(max_length=64, db_index=True)
    serial_number = models.CharField(max_length=128, blank=True, db_index=True)
    case_id = models.UUIDField(null=True, blank=True, db_index=True)
    notes = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    photos = models.JSONField(default=list, blank=True)
    sync_status = models.CharField(max_length=16, default=SYNC_PENDING, db_index=True)
    sync_attempts = models.PositiveSmallIntegerField(default=0)
    last_error = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]


class MobileOperationalAudit(NPTTEBaseModel):
    """Phase 22 — mobile operational audit trail."""

    device = models.ForeignKey(
        DeviceRegistration,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_entries",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mobile_audit_entries",
    )
    action_type = models.CharField(max_length=64, db_index=True)
    payload = models.JSONField(default=dict, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    sync_status = models.CharField(max_length=32, default="synced", db_index=True)
    evidence = models.ForeignKey(
        MobileFieldEvidence,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_links",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["action_type", "created_at"])]
