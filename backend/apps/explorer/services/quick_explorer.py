"""Phase 20A.5 — minimal payloads for instant drawer paint."""
from __future__ import annotations

from apps.explorer.services.context_router import resolve_context_route
from apps.explorer.services.context_summary import build_context_records, build_context_summary
from apps.explorer.services.payloads import list_operational_actions

SLIM_RECORD_KEYS = (
    "id",
    "entity_type",
    "title",
    "severity",
    "status",
    "organisation",
    "organisation_type",
    "address",
    "address_line_2",
    "full_address",
    "city",
    "state",
    "phone",
    "product",
    "batch",
    "serial",
    "detected_at",
    "assigned_officer",
    "recommended_action",
)


def slim_record(row: dict) -> dict:
    if not isinstance(row, dict):
        return {}
    out = {k: row.get(k) for k in SLIM_RECORD_KEYS if row.get(k) not in (None, "")}
    if "id" not in out and row.get("id") is not None:
        out["id"] = row.get("id")
    if "title" not in out:
        out["title"] = row.get("name") or row.get("cluster_code") or row.get("case_reference") or str(row.get("id", ""))
    return out


LITE_SUMMARY_KEYS = frozenset(
    {
        "context_key",
        "entity_type",
        "entity_id",
        "title",
        "summary",
        "count",
        "severity_distribution",
        "status",
        "risk_score",
        "top_states",
        "top_organisations",
        "top_records",
        "updated_at",
        "route",
    }
)


def apply_lite_summary(data: dict) -> dict:
    """Strip optional fields for first-paint payloads (?lite=1)."""
    return {k: v for k, v in data.items() if k in LITE_SUMMARY_KEYS}


def build_quick_summary(*, context_key: str, request=None, lite: bool = False) -> dict:
    base = build_context_summary(context_key=context_key, request=request)
    summary = base.get("summary") if isinstance(base.get("summary"), dict) else {}
    states = base.get("state_distribution") or {}
    records = base.get("top_records") or []
    orgs: list[str] = []
    for r in records:
        if isinstance(r, dict):
            o = r.get("organisation")
            if o and o not in orgs:
                orgs.append(str(o))
    top_states = list(states.keys())[:3]
    preview = [slim_record(r) for r in records[:8] if isinstance(r, dict)]
    out = {
        "context_key": context_key,
        "entity_type": base.get("entity_type"),
        "entity_id": base.get("entity_id"),
        "title": base.get("title"),
        "summary": summary.get("body") or summary.get("title") or base.get("title"),
        "count": base.get("count", 0),
        "severity_distribution": base.get("severity_distribution") or {},
        "status": base.get("risk_status") or summary.get("status"),
        "risk_score": base.get("risk_score"),
        "confidence": summary.get("confidence") or summary.get("confidence_score"),
        "top_states": top_states,
        "top_organisations": orgs[:3],
        "top_records": preview,
        "updated_at": base.get("updated_at"),
        "recommended_actions": base.get("recommended_actions") or [],
    }
    if lite:
        return apply_lite_summary(out)
    return out


def build_quick_records(*, context_key: str, request=None, page: int = 1, page_size: int = 25) -> dict:
    data = build_context_records(
        context_key=context_key,
        request=request,
        page=page,
        page_size=page_size,
    )
    rec_block = data.get("records") or {}
    items = rec_block.get("items") if isinstance(rec_block, dict) else rec_block
    if not isinstance(items, list):
        items = []
    slim_items = [slim_record(r) for r in items if isinstance(r, dict)]
    return {
        "context_key": context_key,
        "entity_type": data.get("entity_type"),
        "entity_id": data.get("entity_id"),
        "records": {
            **rec_block,
            "items": slim_items,
        }
        if isinstance(rec_block, dict)
        else {"items": slim_items, "page": page, "page_size": page_size, "total": len(slim_items), "has_more": False},
    }


def build_quick_bundle(*, context_key: str, request=None, page: int = 1, page_size: int = 25) -> dict:
    """Single aggregate build — summary + records + actions in one pass (fast drawer paint)."""
    from apps.explorer.services.context_aggregates import aggregate_id_for_context, build_context_aggregate_bundle

    aggregate_id = aggregate_id_for_context(context_key)
    bundle = build_context_aggregate_bundle(
        aggregate_id=aggregate_id,
        request=request,
        record_limit=max(page_size, 25),
    )
    records = bundle.get("records") or []
    if isinstance(records, dict):
        records = records.get("items") or []
    if not isinstance(records, list):
        records = []
    slim_items = [slim_record(r) for r in records if isinstance(r, dict)]
    summary = bundle.get("summary") if isinstance(bundle.get("summary"), dict) else {}
    states = bundle.get("state_distribution") or {}
    orgs: list[str] = []
    for r in slim_items:
        o = r.get("organisation")
        if o and o not in orgs:
            orgs.append(str(o))
    route = resolve_context_route(context_key=context_key, user=getattr(request, "user", None))
    actions = list_operational_actions(route["entity_type"], route["entity_id"])
    slim_actions = [
        {
            "id": a.get("id"),
            "label": a.get("label"),
            "workflow": a.get("workflow"),
            "requires_confirm": bool(a.get("requires_confirm")),
        }
        for a in actions
    ]
    from apps.explorer.services.pagination import paginate_list

    return {
        "context_key": context_key,
        "entity_type": bundle.get("entity_type") or "national_risk",
        "entity_id": bundle.get("entity_id") or aggregate_id,
        "title": summary.get("title") or context_key.replace("_", " ").title(),
        "summary": summary.get("body") or summary.get("title") or "",
        "count": bundle.get("record_count") or len(slim_items),
        "severity_distribution": bundle.get("severity_distribution") or {},
        "status": summary.get("severity") or summary.get("status") or bundle.get("risk_status"),
        "risk_score": summary.get("score") or bundle.get("risk_score"),
        "top_states": list(states.keys())[:3],
        "top_organisations": orgs[:3],
        "top_records": slim_items[:8],
        "records": paginate_list(slim_items, page=page, page_size=page_size),
        "actions": slim_actions,
        "updated_at": bundle.get("last_updated"),
        "route": route,
    }


def build_quick_actions(*, context_key: str, request=None) -> dict:
    route = resolve_context_route(context_key=context_key, user=getattr(request, "user", None))
    actions = list_operational_actions(route["entity_type"], route["entity_id"])
    slim = []
    for a in actions:
        slim.append(
            {
                "id": a.get("id"),
                "label": a.get("label"),
                "workflow": a.get("workflow"),
                "requires_confirm": bool(a.get("requires_confirm")),
                "default_priority": "high",
                "default_timeframe": "24h",
                "default_assignee_hint": "Regional supervisor",
            }
        )
    return {"route": route, "actions": slim}
