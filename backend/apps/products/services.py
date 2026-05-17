"""Product and batch regulatory services."""
from __future__ import annotations

from django.utils import timezone

from apps.audit.services import log_api_action
from apps.core.constants import RegulatorBatchStatus, SupplyChainTransactionType, VerificationStatus
from apps.products.models import ProductBatch
from apps.traceability.services import record_supply_chain_transaction


def approve_batch(*, batch: ProductBatch, actor, request=None, notes: str = "") -> ProductBatch:
    """Regulator approval for national batch release."""
    before = {"regulator_status": batch.regulator_status}
    batch.regulator_status = RegulatorBatchStatus.APPROVED
    batch.save(update_fields=["regulator_status", "updated_at"])
    source_org = None
    if batch.manufacturing_site_id:
        source_org = batch.manufacturing_site.manufacturer.organisation
    record_supply_chain_transaction(
        transaction_type=SupplyChainTransactionType.BATCH_CREATED,
        request=request,
        actor=actor,
        source_organisation=source_org,
        product=batch.product,
        batch=batch,
        verification_status=VerificationStatus.VERIFIED,
        notes=notes or f"Batch {batch.batch_number} approved",
    )
    log_api_action(
        request=request,
        actor=actor,
        action="regulatory.batch_approve",
        entity_type="product_batch",
        entity_id=batch.id,
        before_state=before,
        after_state={"regulator_status": batch.regulator_status},
    )
    return batch


def suspend_batch(*, batch: ProductBatch, actor, request=None, reason: str = "") -> ProductBatch:
    before = {"regulator_status": batch.regulator_status}
    batch.regulator_status = RegulatorBatchStatus.SUSPENDED
    batch.save(update_fields=["regulator_status", "updated_at"])
    log_api_action(
        request=request,
        actor=actor,
        action="regulatory.batch_suspend",
        entity_type="product_batch",
        entity_id=batch.id,
        before_state=before,
        after_state={"regulator_status": batch.regulator_status, "reason": reason},
    )
    return batch
