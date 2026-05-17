from django.db import models

from apps.core.constants import EventCategory
from apps.core.models import NPTTEBaseModel
from apps.organisations.models import Organisation


class EventStreamBase(NPTTEBaseModel):
    """Append-only event record — partitioned by category via concrete models."""

    event_id = models.CharField(max_length=64, unique=True, db_index=True)
    category = models.CharField(max_length=32, choices=EventCategory.CHOICES, db_index=True)
    event_type = models.CharField(max_length=64, db_index=True)
    organisation = models.ForeignKey(
        Organisation, on_delete=models.SET_NULL, null=True, blank=True, related_name="%(class)s_events"
    )
    payload = models.JSONField(default=dict, blank=True)
    published_at = models.DateTimeField(db_index=True)
    is_archived = models.BooleanField(default=False, db_index=True)
    sequence_number = models.BigIntegerField(db_index=True)

    class Meta:
        abstract = True
        ordering = ["sequence_number"]


class SystemEvent(EventStreamBase):
    class Meta(EventStreamBase.Meta):
        verbose_name = "System event"


class VerificationEvent(EventStreamBase):
    serial_number = models.CharField(max_length=128, blank=True, db_index=True)

    class Meta(EventStreamBase.Meta):
        verbose_name = "Verification stream event"


class InventoryEvent(EventStreamBase):
    product_id = models.UUIDField(null=True, blank=True, db_index=True)

    class Meta(EventStreamBase.Meta):
        verbose_name = "Inventory stream event"


class EmergencyEvent(EventStreamBase):
    epidemic_code = models.CharField(max_length=64, blank=True, db_index=True)

    class Meta(EventStreamBase.Meta):
        verbose_name = "Emergency stream event"


class FraudEvent(EventStreamBase):
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, db_index=True)

    class Meta(EventStreamBase.Meta):
        verbose_name = "Fraud stream event"
