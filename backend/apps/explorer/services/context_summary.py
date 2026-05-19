"""Phase 20A.4 — lightweight context summaries for instant drawer paint."""
from __future__ import annotations

from apps.explorer.constants import AGGREGATE_IDS
from apps.explorer.services.context_aggregates import (
    aggregate_id_for_context,
    build_context_aggregate_bundle,
)
from apps.explorer.services.pagination import paginate_list


def build_context_summary(*, context_key: str, request=None) -> dict:
    """Title, counts, severity distribution, top records — no full bundle."""
    aggregate_id = aggregate_id_for_context(context_key)
    bundle = build_context_aggregate_bundle(
        aggregate_id=aggregate_id,
        request=request,
        record_limit=25,
    )
    records = bundle.get("records") or []
    if isinstance(records, dict):
        records = records.get("items") or []
    top = records[:5] if isinstance(records, list) else []
    summary = bundle.get("summary") or {}
    return {
        "context_key": context_key,
        "entity_type": bundle.get("entity_type") or "national_risk",
        "entity_id": bundle.get("entity_id") or aggregate_id,
        "title": summary.get("title") or context_key.replace("_", " ").title(),
        "count": bundle.get("record_count") or len(records),
        "severity_distribution": bundle.get("severity_distribution") or {},
        "state_distribution": bundle.get("state_distribution") or {},
        "top_records": top,
        "risk_status": summary.get("severity") or summary.get("status"),
        "risk_score": summary.get("score"),
        "updated_at": bundle.get("last_updated"),
        "summary": summary,
        "recommended_actions": (bundle.get("recommended_actions") or [])[:5],
    }


def build_context_records(
    *,
    context_key: str,
    request=None,
    page: int = 1,
    page_size: int = 25,
) -> dict:
    aggregate_id = aggregate_id_for_context(context_key)
    bundle = build_context_aggregate_bundle(
        aggregate_id=aggregate_id,
        request=request,
        record_limit=100,
    )
    records = bundle.get("records") or []
    if isinstance(records, dict):
        records = records.get("items") or []
    if not isinstance(records, list):
        records = []
    return {
        "context_key": context_key,
        "entity_type": bundle.get("entity_type") or "national_risk",
        "entity_id": bundle.get("entity_id") or aggregate_id,
        "records": paginate_list(records, page=page, page_size=page_size),
    }


def build_light_overview(request, entity_type: str, entity_id: str) -> dict:
    """Fast overview without loading hundreds of records."""
    if entity_id in AGGREGATE_IDS:
        from apps.explorer.services.context_aggregates import build_context_aggregate_bundle

        bundle = build_context_aggregate_bundle(
            aggregate_id=entity_id,
            request=request,
            record_limit=25,
        )
        records = bundle.get("records") or []
        if isinstance(records, dict):
            records = records.get("items") or []
        summary = bundle.get("summary") or {}
        return {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "summary": summary,
            "confidence_score": bundle.get("confidence_score"),
            "tenant_visibility": bundle.get("tenant_visibility"),
            "last_updated": bundle.get("last_updated"),
            "recommended_actions": (bundle.get("recommended_actions") or [])[:5],
            "source_systems": bundle.get("source_systems") or [],
            "is_aggregate": True,
            "record_count": bundle.get("record_count") or len(records),
            "record_preview": records[:5],
            "risk_status": summary.get("severity") or summary.get("status"),
            "risk_score": summary.get("score"),
            "severity_distribution": bundle.get("severity_distribution") or {},
        }
    from apps.explorer.services.payloads import build_explorer_bundle

    full = build_explorer_bundle(request, entity_type, entity_id)
    records = full.get("records") or []
    if isinstance(records, dict):
        records = records.get("items") or []
    summary = full.get("summary") or {}
    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "summary": summary,
        "confidence_score": full.get("confidence_score"),
        "tenant_visibility": full.get("tenant_visibility"),
        "last_updated": full.get("last_updated"),
        "recommended_actions": (full.get("recommended_actions") or [])[:5],
        "source_systems": full.get("source_systems") or [],
        "is_aggregate": False,
        "record_count": len(records) if isinstance(records, list) else 0,
        "record_preview": (records[:5] if isinstance(records, list) else []),
        "risk_status": summary.get("status") or (full.get("risk_explanation") or {}).get("status"),
        "risk_score": summary.get("score") or (full.get("risk_explanation") or {}).get("score"),
    }
