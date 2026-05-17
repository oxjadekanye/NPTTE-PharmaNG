from django.db import models

from apps.core.models import NPTTEBaseModel
from apps.organisations.models import Organisation
from apps.traceability.models import SupplyChainTransaction


class LogisticsProviderProfile(NPTTEBaseModel):
    organisation = models.OneToOneField(
        Organisation,
        on_delete=models.CASCADE,
        related_name="logistics_profile",
    )
    transport_license = models.CharField(max_length=128, blank=True, db_index=True)
    fleet_size = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Logistics provider profile"
        verbose_name_plural = "Logistics provider profiles"


class LogisticsShipment(NPTTEBaseModel):
    """Shipment linking origin, destination, and traceability transaction."""

    tracking_number = models.CharField(max_length=128, unique=True, db_index=True)
    logistics_provider = models.ForeignKey(
        LogisticsProviderProfile,
        on_delete=models.PROTECT,
        related_name="shipments",
    )
    origin_organisation = models.ForeignKey(
        Organisation,
        on_delete=models.PROTECT,
        related_name="outbound_shipments",
    )
    destination_organisation = models.ForeignKey(
        Organisation,
        on_delete=models.PROTECT,
        related_name="inbound_shipments",
    )
    supply_chain_transaction = models.ForeignKey(
        SupplyChainTransaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="shipments",
    )
    departed_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    temperature_controlled = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Logistics shipment"
        verbose_name_plural = "Logistics shipments"
