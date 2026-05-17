from django.conf import settings
from django.db import models

from apps.core.models import NPTTEBaseModel
from apps.organisations.models import Organisation


class GeolocationEvent(NPTTEBaseModel):
    """Captured GPS event for supply chain or verification context."""

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="geolocation_events",
    )
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="geolocation_events",
    )
    event_type = models.CharField(max_length=64, db_index=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    accuracy_meters = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    related_entity_type = models.CharField(max_length=128, blank=True)
    related_entity_id = models.UUIDField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["event_type", "created_at"]),
            models.Index(fields=["latitude", "longitude"]),
        ]
