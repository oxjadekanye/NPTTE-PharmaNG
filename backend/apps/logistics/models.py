from django.db import models

from apps.core.constants import ShipmentLifecycle
from apps.core.models import NPTTEBaseModel
from apps.organisations.models import Organisation
from apps.products.models import ProductBatch
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
    """National pharmaceutical shipment with full chain-of-custody lifecycle."""

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
    lifecycle_status = models.CharField(
        max_length=32,
        choices=ShipmentLifecycle.CHOICES,
        default=ShipmentLifecycle.CREATED,
        db_index=True,
    )
    departed_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    temperature_controlled = models.BooleanField(default=False)
    chain_integrity_verified = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Logistics shipment"
        verbose_name_plural = "Logistics shipments"


class ShipmentItem(NPTTEBaseModel):
    shipment = models.ForeignKey(
        LogisticsShipment,
        on_delete=models.CASCADE,
        related_name="items",
    )
    batch = models.ForeignKey(
        ProductBatch,
        on_delete=models.PROTECT,
        related_name="shipment_items",
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Shipment item"
        verbose_name_plural = "Shipment items"


class ShipmentCheckpoint(NPTTEBaseModel):
    """GPS and condition checkpoint during shipment transit."""

    shipment = models.ForeignKey(
        LogisticsShipment,
        on_delete=models.CASCADE,
        related_name="checkpoints",
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    temperature_celsius = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    condition_notes = models.TextField(blank=True)
    recorded_at = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ["recorded_at"]
        verbose_name = "Shipment checkpoint"
        verbose_name_plural = "Shipment checkpoints"


class DeliveryConfirmation(NPTTEBaseModel):
    shipment = models.OneToOneField(
        LogisticsShipment,
        on_delete=models.CASCADE,
        related_name="delivery_confirmation",
    )
    received_by_name = models.CharField(max_length=255, blank=True)
    confirmed_at = models.DateTimeField(db_index=True)
    quantity_received = models.PositiveIntegerField(default=0)
    rejection_reason = models.TextField(blank=True)

    class Meta:
        verbose_name = "Delivery confirmation"
        verbose_name_plural = "Delivery confirmations"


class ColdChainLog(NPTTEBaseModel):
    shipment = models.ForeignKey(
        LogisticsShipment,
        on_delete=models.CASCADE,
        related_name="cold_chain_logs",
    )
    temperature_celsius = models.DecimalField(max_digits=5, decimal_places=2)
    recorded_at = models.DateTimeField(db_index=True)
    is_breach = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["recorded_at"]
        verbose_name = "Cold chain log"
        verbose_name_plural = "Cold chain logs"


class SmartWarehouse(NPTTEBaseModel):
    """National warehouse intelligence node."""

    organisation = models.ForeignKey(
        Organisation, on_delete=models.CASCADE, related_name="smart_warehouses"
    )
    name = models.CharField(max_length=255)
    warehouse_code = models.CharField(max_length=64, db_index=True)
    state = models.CharField(max_length=128, blank=True, db_index=True)
    capacity_units = models.PositiveIntegerField(default=0)
    utilization_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, db_index=True)
    cold_chain_enabled = models.BooleanField(default=False, db_index=True)

    class Meta:
        unique_together = [("organisation", "warehouse_code")]
        verbose_name = "Smart warehouse"
        verbose_name_plural = "Smart warehouses"


class WarehouseZone(NPTTEBaseModel):
    warehouse = models.ForeignKey(SmartWarehouse, on_delete=models.CASCADE, related_name="zones")
    zone_code = models.CharField(max_length=32, db_index=True)
    temperature_min = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    temperature_max = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = [("warehouse", "zone_code")]


class WarehouseInventorySnapshot(NPTTEBaseModel):
    warehouse = models.ForeignKey(SmartWarehouse, on_delete=models.CASCADE, related_name="snapshots")
    snapshot_at = models.DateTimeField(db_index=True)
    total_units = models.PositiveIntegerField(default=0)
    sku_count = models.PositiveIntegerField(default=0)
    stock_velocity = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    ageing_days_avg = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    class Meta:
        ordering = ["-snapshot_at"]


class TemperatureExcursion(NPTTEBaseModel):
    warehouse = models.ForeignKey(SmartWarehouse, on_delete=models.CASCADE, related_name="excursions")
    zone = models.ForeignKey(WarehouseZone, on_delete=models.SET_NULL, null=True, blank=True)
    temperature_celsius = models.DecimalField(max_digits=5, decimal_places=2)
    recorded_at = models.DateTimeField(db_index=True)
    duration_minutes = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-recorded_at"]


class WarehouseRiskAssessment(NPTTEBaseModel):
    warehouse = models.ForeignKey(SmartWarehouse, on_delete=models.CASCADE, related_name="risk_assessments")
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, db_index=True)
    fraud_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    shortage_probability = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    assessed_at = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ["-assessed_at"]
