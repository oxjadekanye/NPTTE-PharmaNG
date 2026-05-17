"""
National traceability engine service layer.

All medication movements should be recorded via `record_supply_chain_transaction`.
"""
from __future__ import annotations

import logging
import uuid
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.audit.services import log_api_action
from apps.core.constants import RiskLevel, SupplyChainTransactionType, VerificationStatus
from apps.traceability.models import BatchRecall, SupplyChainTransaction

logger = logging.getLogger("nptte.traceability")


def _device_metadata_from_request(request) -> dict[str, Any]:
    if request is None:
        return {}
    return {
        "ip": request.META.get("REMOTE_ADDR"),
        "user_agent": (request.META.get("HTTP_USER_AGENT") or "")[:512],
        "path": request.path,
        "method": request.method,
    }


def _product_metadata(product) -> dict[str, Any]:
    if not product:
        return {}
    return {
        "id": str(product.id),
        "name": product.name,
        "brand_name": product.brand_name,
        "active_ingredient": product.active_ingredient,
        "strength": product.strength,
        "dosage_form": product.dosage_form,
    }


def _batch_metadata(batch) -> dict[str, Any]:
    if not batch:
        return {}
    return {
        "id": str(batch.id),
        "batch_number": batch.batch_number,
        "expiry_date": batch.expiry_date.isoformat() if batch.expiry_date else None,
    }


@transaction.atomic
def record_supply_chain_transaction(
    *,
    transaction_type: str,
    request=None,
    actor=None,
    source_organisation=None,
    destination_organisation=None,
    product=None,
    batch=None,
    product_serial=None,
    quantity_delta: int = 0,
    verification_status: str = VerificationStatus.PENDING,
    latitude=None,
    longitude=None,
    device_metadata: dict | None = None,
    product_metadata: dict | None = None,
    batch_metadata: dict | None = None,
    parent_transaction=None,
    risk_level: str = RiskLevel.LOW,
    risk_score: Decimal = Decimal("0"),
    notes: str = "",
    created_by=None,
) -> SupplyChainTransaction:
    """
    Record an immutable national supply chain transaction.

    Also writes to platform AuditLog when request context is available.
    """
    audit_ref = uuid.uuid4()
    merged_device = {**_device_metadata_from_request(request), **(device_metadata or {})}
    merged_product = {**_product_metadata(product), **(product_metadata or {})}
    merged_batch = {**_batch_metadata(batch), **(batch_metadata or {})}

    if actor is None and request is not None:
        actor = getattr(request, "user", None)
        if actor is not None and not getattr(actor, "is_authenticated", False):
            actor = None

    txn = SupplyChainTransaction.objects.create(
        audit_reference=audit_ref,
        transaction_type=transaction_type,
        actor=actor,
        source_organisation=source_organisation,
        destination_organisation=destination_organisation,
        product=product,
        batch=batch,
        product_serial=product_serial,
        quantity_delta=quantity_delta,
        verification_status=verification_status,
        latitude=latitude,
        longitude=longitude,
        device_metadata=merged_device,
        product_metadata=merged_product,
        batch_metadata=merged_batch,
        parent_transaction=parent_transaction,
        risk_level=risk_level,
        risk_score=risk_score,
        is_immutable=True,
        notes=notes,
        created_by=created_by or actor,
    )

    try:
        log_api_action(
            request=request,
            actor=actor,
            action=f"traceability.{transaction_type}",
            entity_type="supply_chain_transaction",
            entity_id=txn.id,
            after_state={
                "audit_reference": str(audit_ref),
                "transaction_type": transaction_type,
                "quantity_delta": quantity_delta,
            },
        )
    except Exception as exc:
        logger.warning("Audit log failed for transaction %s: %s", audit_ref, exc)

    return txn


def record_pharmacy_stocking(*, inventory_item, request=None, actor=None, quantity: int):
    return record_supply_chain_transaction(
        transaction_type=SupplyChainTransactionType.PHARMACY_STOCKING,
        request=request,
        actor=actor,
        destination_organisation=inventory_item.organisation,
        product=inventory_item.product,
        batch=inventory_item.batch,
        quantity_delta=quantity,
        verification_status=VerificationStatus.VERIFIED,
    )


def record_pharmacy_sale(*, dispensing, request=None, actor=None):
    return record_supply_chain_transaction(
        transaction_type=SupplyChainTransactionType.PHARMACY_SALE,
        request=request,
        actor=actor,
        source_organisation=dispensing.pharmacy,
        destination_organisation=None,
        product=dispensing.product,
        product_serial=dispensing.product_serial,
        quantity_delta=-int(dispensing.quantity_dispensed),
        verification_status=VerificationStatus.VERIFIED,
        latitude=getattr(dispensing.pharmacy, "latitude", None),
        longitude=getattr(dispensing.pharmacy, "longitude", None),
        notes=f"Dispense {dispensing.id}",
    )


def check_batch_recall(batch) -> BatchRecall | None:
    if not batch:
        return None
    return (
        BatchRecall.objects.filter(batch=batch, resolved_at__isnull=True, is_active=True)
        .order_by("-effective_at")
        .first()
    )
