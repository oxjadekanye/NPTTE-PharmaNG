"""
Platform audit log models.
"""
from django.conf import settings
from django.db import models

from apps.core.models import MetadataModel, TimestampedModel, UUIDPrimaryKeyModel


class AuditLog(UUIDPrimaryKeyModel, TimestampedModel, MetadataModel):
    """
    Append-oriented audit record for security and compliance.

    Designed for immutability at application layer; database triggers and
    blockchain anchoring will be added in later phases.
    """

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=128, db_index=True)
    entity_type = models.CharField(max_length=128, db_index=True)
    entity_id = models.UUIDField(db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True)
    before_state = models.JSONField(default=dict, blank=True)
    after_state = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Audit log"
        verbose_name_plural = "Audit logs"
        indexes = [
            models.Index(fields=["entity_type", "entity_id"]),
            models.Index(fields=["action", "created_at"]),
        ]

    def __str__(self):
        return f"{self.action} on {self.entity_type}:{self.entity_id}"
