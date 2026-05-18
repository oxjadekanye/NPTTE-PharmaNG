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

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["device_type", "trust_score"])]


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
