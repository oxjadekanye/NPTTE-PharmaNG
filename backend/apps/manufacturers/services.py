"""Manufacturer ecosystem services — batch issuance and compliance."""
from __future__ import annotations

import hashlib
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.core.constants import RegulatorBatchStatus, SupplyChainTransactionType, VerificationStatus
from apps.manufacturers.models import ManufacturerProfile, ManufacturingSite, RecallNotice
from apps.products.models import Product, ProductBatch
from apps.serialization.services import generate_medication_serial, issue_serials_for_batch
from apps.traceability.services import record_supply_chain_transaction


@transaction.atomic
def create_national_batch(
    *,
    product: Product,
    batch_number: str,
    manufacturing_site: ManufacturingSite,
    quantity_produced: int,
    manufacturing_date=None,
    expiry_date=None,
    actor=None,
    request=None,
) -> ProductBatch:
    """Register a new national product batch with serial range and verification hash."""
    manufacturing_date = manufacturing_date or timezone.now().date()
    payload = f"{product.id}:{batch_number}:{manufacturing_site.id}:{quantity_produced}"
    verification_hash = hashlib.sha256(payload.encode()).hexdigest()

    batch = ProductBatch.objects.create(
        product=product,
        batch_number=batch_number,
        manufacturing_date=manufacturing_date,
        expiry_date=expiry_date,
        manufacturing_site=manufacturing_site,
        quantity_produced=quantity_produced,
        regulator_status=RegulatorBatchStatus.PENDING,
        verification_hash=verification_hash,
        created_by=actor,
    )

    record_supply_chain_transaction(
        transaction_type=SupplyChainTransactionType.BATCH_CREATED,
        request=request,
        actor=actor,
        source_organisation=manufacturing_site.manufacturer.organisation,
        product=product,
        batch=batch,
        quantity_delta=quantity_produced,
        verification_status=VerificationStatus.PENDING,
        batch_metadata={"batch_number": batch_number, "verification_hash": verification_hash},
    )
    return batch


def issue_batch_serials(*, batch: ProductBatch, count: int, actor=None) -> list:
    """Issue NPTTE-format serials for a batch."""
    serials = issue_serials_for_batch(batch=batch, count=count, actor=actor)
    if serials:
        batch.serial_range_start = serials[0].serial_number
        batch.serial_range_end = serials[-1].serial_number
        batch.save(update_fields=["serial_range_start", "serial_range_end", "updated_at"])
    return serials


def update_compliance_score(manufacturer: ManufacturerProfile) -> Decimal:
    records = manufacturer.gmp_records.filter(is_active=True).order_by("-inspection_date")[:5]
    if not records:
        return Decimal("0")
    avg = sum(r.score for r in records) / len(records)
    manufacturer.compliance_score = avg
    manufacturer.save(update_fields=["compliance_score", "updated_at"])
    return avg


def publish_recall_notice(*, manufacturer, batch, product, reason: str, actor=None) -> RecallNotice:
    return RecallNotice.objects.create(
        manufacturer=manufacturer,
        batch=batch,
        product=product,
        reason=reason,
        effective_at=timezone.now(),
        created_by=actor,
    )
