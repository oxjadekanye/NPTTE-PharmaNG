"""Pharmacy traceability — receive batch / dispense serial (Phase 8)."""
from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.core.constants import AvailabilityStatus
from apps.inventory.models import InventoryItem, InventoryMovement
from apps.organisations.models import Organisation
from apps.products.models import ProductBatch
from apps.serialization.models import ProductSerial
from apps.traceability.services import record_pharmacy_stocking, record_serial_dispense_event


@transaction.atomic
def pharmacy_receive_batch_serials(
    *,
    actor,
    organisation_id,
    batch_id,
    serial_ids: list | None,
    quantity: int,
    request=None,
) -> dict:
    """
    Assign serial custody to pharmacy and increase batch stock (inventory).

    Serials must belong to batch and have no custody yet (national first receipt).
    """
    if not organisation_id:
        raise ValidationError("User must belong to a pharmacy organisation.")
    if quantity < 1 and not serial_ids:
        raise ValidationError("Provide quantity or serial_ids.")
    org = Organisation.objects.get(pk=organisation_id)
    batch = ProductBatch.objects.select_related("product").get(pk=batch_id)
    if serial_ids:
        serials = list(
            ProductSerial.objects.select_for_update()
            .filter(batch=batch, id__in=serial_ids, custody_organisation__isnull=True, is_dispensed=False)
            .order_by("serial_number")
        )
        if len(serials) != len(serial_ids):
            raise ValidationError("Some serials are invalid, already held, or dispensed.")
    else:
        serials = list(
            ProductSerial.objects.select_for_update()
            .filter(batch=batch, custody_organisation__isnull=True, is_dispensed=False)
            .order_by("serial_number")[:quantity]
        )
        if len(serials) < quantity:
            raise ValidationError("Not enough unreceived serials for this batch.")
    now = timezone.now()
    for s in serials:
        s.custody_organisation = org
        s.custody_updated_at = now
        s.custody_updated_by = actor
        s.save(update_fields=["custody_organisation", "custody_updated_at", "custody_updated_by", "updated_at"])

    item, _ = InventoryItem.objects.get_or_create(
        organisation=org,
        product=batch.product,
        batch=batch,
        defaults={
            "quantity_on_hand": 0,
            "availability_status": AvailabilityStatus.OUT_OF_STOCK,
            "created_by": actor,
        },
    )
    delta = len(serials)
    item.quantity_on_hand += delta
    item.last_restocked_at = now
    item.availability_status = (
        AvailabilityStatus.IN_STOCK if item.quantity_on_hand > 10 else AvailabilityStatus.LOW_STOCK
    )
    item.save(update_fields=["quantity_on_hand", "availability_status", "last_restocked_at", "updated_at"])
    InventoryMovement.objects.create(
        inventory_item=item,
        movement_type="pharmacy_batch_receipt",
        quantity_delta=delta,
        reference=str(batch.id),
        notes="NPTTE traceability receive",
        created_by=actor,
    )
    record_pharmacy_stocking(inventory_item=item, request=request, actor=actor, quantity=delta)
    return {"received": delta, "inventory_item_id": str(item.id)}


@transaction.atomic
def pharmacy_dispense_serial(*, actor, organisation_id, serial_number: str, request=None) -> ProductSerial:
    """Mark serial dispensed and decrement pharmacy inventory."""
    if not organisation_id:
        raise ValidationError("User must belong to a pharmacy organisation.")
    org = Organisation.objects.get(pk=organisation_id)
    try:
        serial = ProductSerial.objects.select_for_update().select_related("batch", "batch__product").get(
            serial_number=serial_number.strip()
        )
    except ProductSerial.DoesNotExist as exc:
        raise ValidationError("Serial not found in national registry.") from exc
    if serial.is_dispensed:
        raise ValidationError("Serial already dispensed.")
    if not serial.custody_organisation_id or str(serial.custody_organisation_id) != str(organisation_id):
        raise ValidationError("Serial is not in custody of this pharmacy.")
    item = (
        InventoryItem.objects.select_for_update()
        .filter(organisation=org, product=serial.batch.product, batch=serial.batch, is_active=True)
        .first()
    )
    if not item or item.quantity_on_hand < 1:
        raise ValidationError("No stock on hand for this batch.")
    serial.is_dispensed = True
    serial.save(update_fields=["is_dispensed", "updated_at"])
    item.quantity_on_hand -= 1
    if item.quantity_on_hand == 0:
        item.availability_status = AvailabilityStatus.OUT_OF_STOCK
    elif item.quantity_on_hand <= 10:
        item.availability_status = AvailabilityStatus.LOW_STOCK
    else:
        item.availability_status = AvailabilityStatus.IN_STOCK
    item.save(update_fields=["quantity_on_hand", "availability_status", "updated_at"])
    InventoryMovement.objects.create(
        inventory_item=item,
        movement_type="pharmacy_serial_dispense",
        quantity_delta=-1,
        reference=serial.serial_number,
        notes="NPTTE dispense",
        created_by=actor,
    )
    record_serial_dispense_event(product_serial=serial, source_organisation=org, actor=actor, request=request)
    return serial
