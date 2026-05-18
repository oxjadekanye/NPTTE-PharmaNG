"""Phase 10 — national chain-of-custody ledger."""
from __future__ import annotations

import hashlib

from django.db import transaction
from django.utils import timezone

from apps.traceability.models import SerialCustodyEvent


@transaction.atomic
def record_custody_transfer(
    *,
    product_serial,
    destination_node: str,
    source_node: str = "",
    source_organisation=None,
    destination_organisation=None,
    latitude=None,
    longitude=None,
    supply_chain_transaction=None,
    actor=None,
    confirm: bool = False,
) -> SerialCustodyEvent:
    sig_payload = f"{product_serial.serial_number}:{destination_node}:{timezone.now().isoformat()}"
    signature = hashlib.sha256(sig_payload.encode()).hexdigest()
    event = SerialCustodyEvent.objects.create(
        product_serial=product_serial,
        source_node=source_node,
        destination_node=destination_node,
        source_organisation=source_organisation,
        destination_organisation=destination_organisation,
        latitude=latitude,
        longitude=longitude,
        verification_signature=signature,
        custody_confirmed=confirm,
        integrity_status="verified" if confirm else "pending",
        supply_chain_transaction=supply_chain_transaction,
        created_by=actor,
    )
    if destination_organisation_id:
        product_serial.custody_organisation = destination_organisation
        product_serial.custody_updated_at = timezone.now()
        product_serial.custody_updated_by = actor
        product_serial.save(
            update_fields=["custody_organisation", "custody_updated_at", "custody_updated_by", "updated_at"]
        )
    return event


def custody_timeline_for_serial(*, product_serial) -> list[dict]:
    events = product_serial.custody_events.select_related(
        "source_organisation", "destination_organisation"
    ).order_by("created_at")
    return [
        {
            "at": e.created_at.isoformat(),
            "source_node": e.source_node,
            "destination_node": e.destination_node,
            "source_org": getattr(e.source_organisation, "legal_name", None),
            "destination_org": getattr(e.destination_organisation, "legal_name", None),
            "latitude": str(e.latitude) if e.latitude is not None else None,
            "longitude": str(e.longitude) if e.longitude is not None else None,
            "custody_confirmed": e.custody_confirmed,
            "integrity_status": e.integrity_status,
            "verification_signature": e.verification_signature[:16] + "…",
        }
        for e in events
    ]
