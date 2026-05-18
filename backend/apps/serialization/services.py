"""Serialization and sovereign serial issuance services."""
from __future__ import annotations

import hashlib
import re

from django.db import transaction
from django.utils import timezone

from apps.core.security import sign_verification_token
from apps.serialization.models import ProductSerial, SerialSequence


def _product_slug(product) -> str:
    name = (product.name or product.brand_name or "MED").upper()
    slug = re.sub(r"[^A-Z0-9]+", "-", name).strip("-")
    return slug[:24] or "MED"


def _product_code_segment(product) -> str:
    """Prefer national product code for NG-NPTTE-{PRODUCTCODE}-{YEAR}-{SEQ} (Phase 8)."""
    code = (getattr(product, "national_product_code", None) or "").strip().upper()
    code = re.sub(r"[^A-Z0-9]+", "-", code).strip("-")
    if code:
        return code[:24]
    return _product_slug(product)


@transaction.atomic
def generate_medication_serial(*, product, year: int | None = None) -> str:
    """
    Generate globally unique NPTTE pharmaceutical serial.

    Format: NG-NPTTE-{PRODUCT}-{YEAR}-{SEQUENCE}
    Example: NG-NPTTE-PARACETAMOL-2026-000000001
    """
    year = year or timezone.now().year
    seq_row, _ = SerialSequence.objects.select_for_update().get_or_create(
        product=product,
        year=year,
        defaults={"last_sequence": 0},
    )
    seq_row.last_sequence += 1
    seq_row.save(update_fields=["last_sequence", "updated_at"])
    return f"NG-NPTTE-{_product_code_segment(product)}-{year}-{seq_row.last_sequence:09d}"


def build_qr_payload(serial: ProductSerial) -> str:
    from django.conf import settings

    base = getattr(settings, "NPTTE_VERIFY_BASE_URL", "https://verify.nptte.gov.ng")
    return f"{base}/v1/{serial.serial_number}"


def build_barcode_payload(serial_number: str) -> str:
    return serial_number.replace("-", "")[:32]


def ensure_qr_payload(serial: ProductSerial) -> ProductSerial:
    if not serial.qr_payload:
        serial.qr_payload = build_qr_payload(serial)
    if not serial.barcode_payload:
        serial.barcode_payload = build_barcode_payload(serial.serial_number)
    token_payload = {"serial": serial.serial_number, "batch_id": str(serial.batch_id)}
    serial.qr_token_signature = sign_verification_token(token_payload)
    serial.verification_hash = hashlib.sha256(serial.serial_number.encode()).hexdigest()
    serial.save(
        update_fields=[
            "qr_payload",
            "barcode_payload",
            "qr_token_signature",
            "verification_hash",
            "updated_at",
        ]
    )
    return serial


@transaction.atomic
def issue_serials_for_batch(*, batch, count: int, actor=None) -> list[ProductSerial]:
    """Issue count serials for a batch using national format."""
    serials = []
    for _ in range(count):
        serial_number = generate_medication_serial(product=batch.product)
        serial = ProductSerial.objects.create(
            batch=batch,
            serial_number=serial_number,
            created_by=actor,
        )
        ensure_qr_payload(serial)
        serials.append(serial)
    return serials


def generate_serial_for_batch(*, batch, prefix: str = "NG") -> ProductSerial:
    """Backward-compatible single serial issuance."""
    serials = issue_serials_for_batch(batch=batch, count=1)
    return serials[0]
