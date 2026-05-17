"""Logistics chain-of-custody services."""
from __future__ import annotations

from django.utils import timezone

from apps.core.constants import AlertCategory, AlertSeverity, ShipmentLifecycle, SupplyChainTransactionType
from apps.logistics.models import ColdChainLog, LogisticsShipment, ShipmentCheckpoint
from apps.traceability.services import record_supply_chain_transaction


def record_shipment_checkpoint(
    *,
    shipment: LogisticsShipment,
    latitude,
    longitude,
    temperature_celsius=None,
    condition_notes: str = "",
    request=None,
    actor=None,
) -> ShipmentCheckpoint:
    checkpoint = ShipmentCheckpoint.objects.create(
        shipment=shipment,
        latitude=latitude,
        longitude=longitude,
        temperature_celsius=temperature_celsius,
        condition_notes=condition_notes,
        recorded_at=timezone.now(),
        created_by=actor,
    )

    if shipment.temperature_controlled and temperature_celsius is not None:
        is_breach = float(temperature_celsius) > 8.0 or float(temperature_celsius) < 2.0
        ColdChainLog.objects.create(
            shipment=shipment,
            temperature_celsius=temperature_celsius,
            recorded_at=timezone.now(),
            is_breach=is_breach,
            created_by=actor,
        )
        if is_breach:
            from apps.alerts.services import create_national_alert
            from decimal import Decimal

            create_national_alert(
                alert_type=AlertCategory.COLD_CHAIN_BREACH,
                title=f"Cold chain breach: {shipment.tracking_number}",
                description=condition_notes or "Temperature out of range.",
                severity=AlertSeverity.CRITICAL,
                risk_score=Decimal("80"),
                organisation=shipment.destination_organisation,
            )

    if shipment.lifecycle_status == ShipmentLifecycle.CREATED:
        shipment.lifecycle_status = ShipmentLifecycle.IN_TRANSIT
        shipment.departed_at = timezone.now()
        shipment.save(update_fields=["lifecycle_status", "departed_at", "updated_at"])

    record_supply_chain_transaction(
        transaction_type=SupplyChainTransactionType.WAREHOUSE_TRANSFER,
        request=request,
        actor=actor,
        source_organisation=shipment.origin_organisation,
        destination_organisation=shipment.destination_organisation,
        latitude=latitude,
        longitude=longitude,
        notes=f"Checkpoint {shipment.tracking_number}",
    )
    return checkpoint
