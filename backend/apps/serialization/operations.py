"""Phase 10 — serialization operations: scans, packaging, labels."""
from __future__ import annotations

import uuid
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.serialization.gs1 import decode_gs1_scan
from apps.serialization.models import ProductSerial, SerialPackagingUnit, SerialScanRecord


@transaction.atomic
def record_serial_scan(
    *,
    raw_scan: str,
    scan_source: str,
    scanner_type: str = "",
    outcome: str = "",
    latitude=None,
    longitude=None,
    device_fingerprint: str = "",
    replay_nonce: str = "",
    actor=None,
) -> SerialScanRecord:
    decoded = decode_gs1_scan(raw_scan)
    serial_number = decoded.national_serial or decoded.serial or raw_scan.strip()
    product_serial = ProductSerial.objects.filter(serial_number=serial_number).first()

    duplicate = False
    if replay_nonce:
        duplicate = SerialScanRecord.objects.filter(replay_nonce=replay_nonce).exists()
    elif device_fingerprint:
        duplicate = SerialScanRecord.objects.filter(
            serial_number=serial_number,
            device_fingerprint=device_fingerprint,
            created_at__gte=timezone.now() - timedelta(minutes=2),
        ).exists()

    suspicious = duplicate or outcome in ("counterfeit_suspected", "suspicious", "invalid_serial")

    record = SerialScanRecord.objects.create(
        product_serial=product_serial,
        serial_number=serial_number,
        scan_source=scan_source,
        scanner_type=scanner_type,
        outcome=outcome,
        latitude=latitude,
        longitude=longitude,
        device_fingerprint=device_fingerprint,
        replay_nonce=replay_nonce,
        is_duplicate=duplicate,
        is_suspicious=suspicious,
        scan_metadata={"decoded": decoded.__dict__, "raw": raw_scan[:512]},
        created_by=actor,
    )

    if product_serial and suspicious:
        from apps.ai_engine.services import calculate_counterfeit_probability

        prob = calculate_counterfeit_probability(serial_number=serial_number)
        product_serial.counterfeit_probability = prob
        product_serial.save(update_fields=["counterfeit_probability", "updated_at"])

    return record


@transaction.atomic
def create_packaging_unit(*, batch, level: str, parent=None, serial_ids=None, actor=None) -> SerialPackagingUnit:
    pack_code = f"NPTTE-PKG-{level.upper()}-{uuid.uuid4().hex[:12].upper()}"
    unit = SerialPackagingUnit.objects.create(
        batch=batch,
        pack_code=pack_code,
        level=level,
        parent=parent,
        created_by=actor,
    )
    if serial_ids:
        qs = ProductSerial.objects.filter(id__in=serial_ids, batch=batch)
        count = qs.update(packaging_unit=unit)
        unit.serial_count = count
        unit.save(update_fields=["serial_count", "updated_at"])
    return unit


def build_printable_label(*, product_serial: ProductSerial) -> dict:
    """Structured label payload for PDF/print renderers (client or future service)."""
    batch = product_serial.batch
    product = batch.product
    return {
        "serial_number": product_serial.serial_number,
        "qr_payload": product_serial.qr_payload,
        "barcode_payload": product_serial.barcode_payload,
        "gs1_element_string": product_serial.gs1_element_string,
        "gtin14": product_serial.gtin14,
        "product_name": product.name,
        "batch_number": batch.batch_number,
        "expiry_date": str(batch.expiry_date) if batch.expiry_date else "",
        "manufacturer": getattr(product.manufacturer, "legal_name", "") if product.manufacturer_id else "",
        "issued_at": timezone.now().isoformat(),
        "national_mark": "NPTTE SOVEREIGN SERIALIZATION",
    }
