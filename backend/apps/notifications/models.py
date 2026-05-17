"""
Notification models.
"""
from django.conf import settings
from django.db import models

from apps.core.models import NPTTEBaseModel


class Notification(NPTTEBaseModel):
    """
    Platform notification to a user or role cohort.

    Delivery channels and read receipts will be extended in later phases.
    """

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    channel = models.CharField(max_length=32, default="in_app", db_index=True)
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    related_entity_type = models.CharField(max_length=128, blank=True)
    related_entity_id = models.UUIDField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return self.title
