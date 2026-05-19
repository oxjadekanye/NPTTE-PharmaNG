"""Phase 20A — lightweight explorer overview payloads (fast drawer first paint)."""
from __future__ import annotations

from apps.explorer.constants import AGGREGATE_IDS
from apps.explorer.services.payloads import build_explorer_bundle


def build_explorer_overview(request, entity_type: str, entity_id: str) -> dict:
    """Summary + metadata only — no heavy records/timeline."""
    full = build_explorer_bundle(request, entity_type, entity_id)
    records = full.get("records") or []
    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "summary": full.get("summary") or {},
        "confidence_score": full.get("confidence_score"),
        "tenant_visibility": full.get("tenant_visibility"),
        "last_updated": full.get("last_updated"),
        "recommended_actions": full.get("recommended_actions") or [],
        "source_systems": full.get("source_systems") or [],
        "is_aggregate": entity_id in AGGREGATE_IDS,
        "record_count": len(records),
        "record_preview": records[:5],
        "risk_status": (full.get("summary") or {}).get("status") or (full.get("risk_explanation") or {}).get("status"),
        "risk_score": (full.get("summary") or {}).get("score") or (full.get("risk_explanation") or {}).get("score"),
    }


def paginate_list(items: list, *, page: int = 1, page_size: int = 25) -> dict:
    page = max(1, page)
    page_size = min(100, max(1, page_size))
    start = (page - 1) * page_size
    end = start + page_size
    slice_items = items[start:end]
    total = len(items)
    return {
        "items": slice_items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "has_more": end < total,
    }
