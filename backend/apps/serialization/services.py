"""Serialization and QR identity services."""
from __future__ import annotations

import uuid

from django.conf import settings

from apps.serialization.models import ProductSerial


def build_qr_payload(serial: ProductSerial) -> str:
    """Build verification URL/payload for a product serial."""
    base = getattr(settings, "NPTTE_VERIFY_BASE_URL", "https://verify.nptte.gov.ng")
    return f"{base}/v1/{serial.serial_number}"


def ensure_qr_payload(serial: ProductSerial) -> ProductSerial:
    if not serial.qr_payload:
        serial.qr_payload = build_qr_payload(serial)
        serial.save(update_fields=["qr_payload", "updated_at"])
    return serial


def generate_serial_for_batch(*, batch, prefix: str = "NG") -> ProductSerial:
    serial_number = f"{prefix}-{uuid.uuid4().hex[:12].upper()}"
    serial = ProductSerial.objects.create(
        batch=batch,
        serial_number=serial_number,
    )
    ensure_qr_payload(serial)
    return serial
