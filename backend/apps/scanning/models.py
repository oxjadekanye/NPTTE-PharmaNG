"""Phase 12 — national scan event ledger for mobile operations."""
from django.conf import settings
from django.db import models

from apps.core.models import NPTTEBaseModel
from apps.organisations.models import Organisation


class ScanEvent(NPTTEBaseModel):
    SCAN_CITIZEN = "citizen_verify"
    SCAN_PHARMACY_RECEIVE = "pharmacy_receive"
    SCAN_PHARMACY_DISPENSE = "pharmacy_dispense"
    SCAN_REGULATOR = "regulator_inspection"
    SCAN_CUSTOMS = "customs_verify"
    SCAN_WAREHOUSE = "warehouse_receive"
    SCAN_TYPE_CHOICES = [
        (SCAN_CITIZEN, "Citizen verification"),
        (SCAN_PHARMACY_RECEIVE, "Pharmacy receive"),
        (SCAN_PHARMACY_DISPENSE, "Pharmacy dispense"),
        (SCAN_REGULATOR, "Regulator inspection"),
        (SCAN_CUSTOMS, "Customs verification"),
        (SCAN_WAREHOUSE, "Warehouse receive"),
    ]

    SYNC_PENDING = "pending"
    SYNC_SYNCED = "synced"
    SYNC_FAILED = "failed"
    SYNC_CHOICES = [
        (SYNC_PENDING, "Pending"),
        (SYNC_SYNCED, "Synced"),
        (SYNC_FAILED, "Failed"),
    ]

    serial_number = models.CharField(max_length=128, db_index=True)
    scan_type = models.CharField(max_length=64, choices=SCAN_TYPE_CHOICES, db_index=True)
    actor_role = models.CharField(max_length=64, blank=True, db_index=True)
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="scan_events",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="scan_events",
    )
    device_id = models.CharField(max_length=128, blank=True, db_index=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    offline_timestamp = models.DateTimeField(null=True, blank=True, db_index=True)
    sync_status = models.CharField(max_length=32, choices=SYNC_CHOICES, default=SYNC_SYNCED, db_index=True)
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, db_index=True)
    outcome_label = models.CharField(max_length=64, blank=True, db_index=True)
    result_payload = models.JSONField(default=dict, blank=True)
    replay_nonce = models.CharField(max_length=64, blank=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["serial_number", "created_at"]),
            models.Index(fields=["scan_type", "sync_status"]),
        ]
