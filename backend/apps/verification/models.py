"""
Medicine verification event models.
"""
from django.db import models

from apps.core.constants import VerificationChannel
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
