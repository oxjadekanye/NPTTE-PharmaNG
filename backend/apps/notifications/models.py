"""
Notification models.
"""
from django.conf import settings
from django.db import models

from apps.core.models import NPTTEBaseModel
from apps.notifications.constants import SEVERITY_CHOICES, SEVERITY_INFO
from apps.organisations.models import Organisation


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
    severity = models.CharField(max_length=16, choices=SEVERITY_CHOICES, default=SEVERITY_INFO, db_index=True)
    notification_type = models.CharField(max_length=64, blank=True, db_index=True)
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
    )
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    email_status = models.CharField(max_length=32, default="skipped", db_index=True)
    related_entity_type = models.CharField(max_length=128, blank=True)
    related_entity_id = models.UUIDField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        indexes = [
            models.Index(fields=["recipient", "is_read", "-created_at"]),
            models.Index(fields=["organisation", "-created_at"]),
        ]

    def __str__(self):
        return self.title
