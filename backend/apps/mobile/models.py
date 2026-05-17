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
