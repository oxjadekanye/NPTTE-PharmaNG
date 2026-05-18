"""Product and batch regulatory services."""
from __future__ import annotations

from django.utils import timezone

from apps.audit.services import log_api_action
from apps.core.constants import (
    BatchLifecycleStatus,
    BatchRegulatoryAuditAction,
    RegulatorBatchStatus,
    SupplyChainTransactionType,
    VerificationStatus,
)
from apps.products.models import ProductBatch
from apps.traceability.models import BatchRecall
from apps.traceability.regulatory_audit import log_batch_regulatory_audit
from apps.traceability.services import record_supply_chain_transaction


def approve_batch(*, batch: ProductBatch, actor, request=None, notes: str = "") -> ProductBatch:
    """Regulator approval for national batch release."""
    before = {"regulator_status": batch.regulator_status, "lifecycle_status": batch.lifecycle_status}
    batch.regulator_status = RegulatorBatchStatus.APPROVED
    batch.lifecycle_status = BatchLifecycleStatus.APPROVED
    batch.save(update_fields=["regulator_status", "lifecycle_status", "updated_at"])
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
        after_state={"regulator_status": batch.regulator_status, "lifecycle_status": batch.lifecycle_status},
    )
    log_batch_regulatory_audit(
        batch=batch,
        action=BatchRegulatoryAuditAction.APPROVED,
        actor=actor,
        notes=notes,
        payload={"regulator_status": batch.regulator_status},
    )
    return batch


def suspend_batch(*, batch: ProductBatch, actor, request=None, reason: str = "") -> ProductBatch:
    before = {"regulator_status": batch.regulator_status, "lifecycle_status": batch.lifecycle_status}
    batch.regulator_status = RegulatorBatchStatus.SUSPENDED
    batch.lifecycle_status = BatchLifecycleStatus.SUSPENDED
    batch.save(update_fields=["regulator_status", "lifecycle_status", "updated_at"])
    log_api_action(
        request=request,
        actor=actor,
        action="regulatory.batch_suspend",
        entity_type="product_batch",
        entity_id=batch.id,
        before_state=before,
        after_state={"regulator_status": batch.regulator_status, "lifecycle_status": batch.lifecycle_status, "reason": reason},
    )
    log_batch_regulatory_audit(
        batch=batch,
        action=BatchRegulatoryAuditAction.SUSPENDED,
        actor=actor,
        notes=reason,
    )
    return batch


def reject_batch(*, batch: ProductBatch, actor, request=None, reason: str = "") -> ProductBatch:
    """Regulator rejection — batch returns to draft lifecycle for manufacturer correction."""
    before = {"regulator_status": batch.regulator_status, "lifecycle_status": batch.lifecycle_status}
    batch.regulator_status = RegulatorBatchStatus.REJECTED
    batch.lifecycle_status = BatchLifecycleStatus.DRAFT
    batch.save(update_fields=["regulator_status", "lifecycle_status", "updated_at"])
    log_api_action(
        request=request,
        actor=actor,
        action="regulatory.batch_reject",
        entity_type="product_batch",
        entity_id=batch.id,
        before_state=before,
        after_state={"regulator_status": batch.regulator_status, "lifecycle_status": batch.lifecycle_status, "reason": reason},
    )
    log_batch_regulatory_audit(
        batch=batch,
        action=BatchRegulatoryAuditAction.REJECTED,
        actor=actor,
        notes=reason,
    )
    return batch


def issue_national_batch_recall(
    *,
    batch: ProductBatch,
    actor,
    request=None,
    reason: str,
    issued_by_organisation=None,
) -> BatchRecall:
    """
    National recall enforcement: registry entry + batch lifecycle + supply-chain record.
    """
    batch.lifecycle_status = BatchLifecycleStatus.RECALLED
    batch.save(update_fields=["lifecycle_status", "updated_at"])
    recall = BatchRecall.objects.create(
        batch=batch,
        recall_reason=reason,
        issued_by_organisation=issued_by_organisation,
        effective_at=timezone.now(),
        created_by=actor,
    )
    record_supply_chain_transaction(
        transaction_type=SupplyChainTransactionType.RECALL,
        request=request,
        actor=actor,
        product=batch.product,
        batch=batch,
        quantity_delta=0,
        verification_status=VerificationStatus.RECALLED,
        notes=reason,
    )
    log_api_action(
        request=request,
        actor=actor,
        action="regulatory.batch_recall",
        entity_type="product_batch",
        entity_id=batch.id,
        after_state={"lifecycle_status": batch.lifecycle_status, "recall_id": str(recall.id)},
    )
    log_batch_regulatory_audit(
        batch=batch,
        action=BatchRegulatoryAuditAction.RECALLED,
        actor=actor,
        notes=reason,
        payload={"recall_id": str(recall.id)},
    )
    return recall


def mark_batch_destroyed(*, batch: ProductBatch, actor, request=None, notes: str = "") -> ProductBatch:
    batch.lifecycle_status = BatchLifecycleStatus.DESTROYED
    batch.save(update_fields=["lifecycle_status", "updated_at"])
    log_batch_regulatory_audit(
        batch=batch,
        action=BatchRegulatoryAuditAction.DESTROYED,
        actor=actor,
        notes=notes,
    )
    log_api_action(
        request=request,
        actor=actor,
        action="regulatory.batch_destroyed",
        entity_type="product_batch",
        entity_id=batch.id,
        after_state={"lifecycle_status": batch.lifecycle_status},
    )
    return batch
