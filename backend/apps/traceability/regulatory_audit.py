"""Batch regulatory audit trail helpers (Phase 8)."""
from __future__ import annotations

from apps.traceability.models import BatchRegulatoryAudit


def log_batch_regulatory_audit(
    *,
    batch,
    action: str,
    actor=None,
    notes: str = "",
    payload: dict | None = None,
):
    """Append an immutable batch regulatory audit row."""
    return BatchRegulatoryAudit.objects.create(
        batch=batch,
        action=action,
        actor=actor,
        notes=notes or "",
        payload=payload or {},
        created_by=actor,
    )
