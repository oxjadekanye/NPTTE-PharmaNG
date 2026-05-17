"""
Abstract base models for NPTTE domain entities.

All persistent records inherit consistent identifiers, audit timestamps,
soft lifecycle flags, and extensible metadata for national-scale integration.
"""
import uuid

from django.conf import settings
from django.db import models

from apps.core.constants import RecordStatus


class UUIDPrimaryKeyModel(models.Model):
    """UUID primary key for distributed, government-grade identifier stability."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimestampedModel(models.Model):
    """Automatic created/updated timestamps."""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AuditedModel(models.Model):
    """Tracks which platform user created or last influenced a record."""

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created",
    )

    class Meta:
        abstract = True


class LifecycleModel(models.Model):
    """Standard active flag and status for operational records."""

    is_active = models.BooleanField(default=True, db_index=True)
    status = models.CharField(
        max_length=32,
        choices=RecordStatus.CHOICES,
        default=RecordStatus.ACTIVE,
        db_index=True,
    )

    class Meta:
        abstract = True


class MetadataModel(models.Model):
    """JSON metadata for integration payloads without schema churn."""

    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        abstract = True


class NPTTEBaseModel(
    UUIDPrimaryKeyModel,
    TimestampedModel,
    AuditedModel,
    LifecycleModel,
    MetadataModel,
):
    """
    Foundation mixin for NPTTE domain models.

    Combines UUID identity, audit fields, lifecycle management, and metadata.
    """

    class Meta:
        abstract = True
