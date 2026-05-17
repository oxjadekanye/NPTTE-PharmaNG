"""
Medicine verification event models.
"""
from django.db import models

from apps.core.constants import VerificationChannel, VerificationOutcome
from apps.core.models import NPTTEBaseModel
from apps.serialization.models import ProductSerial


class VerificationEvent(NPTTEBaseModel):
    """
    Public or authenticated verification attempt against a serialised unit.

    Records channel, outcome, and client context for fraud analytics (future AI layer).
    """

    product_serial = models.ForeignKey(
        ProductSerial,
        on_delete=models.PROTECT,
        related_name="verification_events",
    )
    channel = models.CharField(
        max_length=16,
        choices=VerificationChannel.CHOICES,
        db_index=True,
    )
    is_authentic = models.BooleanField(null=True, blank=True)
    verification_message = models.CharField(max_length=512, blank=True)
    client_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Verification event"
        verbose_name_plural = "Verification events"

    def __str__(self):
        return f"{self.channel} — {self.product_serial}"


class VerificationScanLog(NPTTEBaseModel):
    """Sovereign verification scan log with geolocation and device intelligence."""

    product_serial = models.ForeignKey(
        ProductSerial,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="scan_logs",
    )
    serial_number = models.CharField(max_length=128, db_index=True)
    outcome = models.CharField(
        max_length=32,
        choices=VerificationOutcome.CHOICES,
        db_index=True,
    )
    qr_token = models.CharField(max_length=512, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    device_fingerprint = models.CharField(max_length=64, blank=True, db_index=True)
    client_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True)
    scan_metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["serial_number", "created_at"]),
            models.Index(fields=["outcome", "created_at"]),
            models.Index(fields=["device_fingerprint", "created_at"]),
        ]
        verbose_name = "Verification scan log"
        verbose_name_plural = "Verification scan logs"
