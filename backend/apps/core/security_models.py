"""Enterprise security threat logging."""
from django.db import models

from apps.core.models import NPTTEBaseModel


class SecurityThreatLog(NPTTEBaseModel):
    """Immutable security incident log for regulator review."""

    threat_type = models.CharField(max_length=64, db_index=True)
    severity = models.CharField(max_length=16, db_index=True)
    request_fingerprint = models.CharField(max_length=64, db_index=True, blank=True)
    client_ip = models.GenericIPAddressField(null=True, blank=True)
    endpoint = models.CharField(max_length=255, blank=True)
    user_agent = models.CharField(max_length=512, blank=True)
    details = models.JSONField(default=dict, blank=True)
    is_blocked = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["threat_type", "created_at"]),
            models.Index(fields=["request_fingerprint", "created_at"]),
        ]
        verbose_name = "Security threat log"
        verbose_name_plural = "Security threat logs"
