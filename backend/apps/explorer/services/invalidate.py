"""Phase 20A — targeted cache invalidation hooks."""
from __future__ import annotations

from apps.explorer.services.cache import invalidate_context, invalidate_entity, invalidate_scope
from apps.explorer.services.context_aggregates import aggregate_id_for_context

# Streambus event prefix -> dashboard context keys to invalidate
_EVENT_CONTEXT_MAP: dict[str, tuple[str, ...]] = {
    "alert.": ("open_alerts", "national_status", "urgent_actions"),
    "scan.": ("counterfeit_detections", "verifications_24h", "national_verifications"),
    "recall.": ("recalls", "emergency_recalls"),
    "enforcement.": ("active_investigations", "enforcement_readiness", "fraud_flags"),
    "intelligence.": ("fraud_flags", "national_ai_intelligence"),
    "customs.": ("customs_holds", "import_disruption"),
}


def _contexts_for_event(event_type: str) -> tuple[str, ...]:
    for prefix, keys in _EVENT_CONTEXT_MAP.items():
        if event_type.startswith(prefix):
            return keys
    return ()


def on_streambus_event(*, event_type: str, payload: dict | None = None) -> None:
    payload = payload or {}
    for ctx in _contexts_for_event(event_type):
        invalidate_context(ctx)
    et = payload.get("explorer_entity_type")
    eid = payload.get("explorer_entity_id")
    if et and eid:
        invalidate_entity(str(et), str(eid))
        ctx_key = payload.get("context_key") or payload.get("explorer_context")
        if ctx_key:
            invalidate_context(str(ctx_key))
    if event_type.startswith("enforcement."):
        invalidate_scope("detail")
        invalidate_scope("timeline")


def on_enforcement_mutation(*, entity_type: str = "enforcement_case", entity_id: str | None = None) -> None:
    invalidate_context("active_investigations")
    invalidate_context("enforcement_readiness")
    invalidate_scope("detail")
    invalidate_scope("timeline")
    invalidate_scope("overview")
    if entity_id:
        invalidate_entity(entity_type, str(entity_id))


def on_investigation_update(*, case_id: str | None = None) -> None:
    on_enforcement_mutation(entity_type="enforcement_case", entity_id=case_id)


def on_recommendation_change(*, recommendation_id: str | None = None) -> None:
    invalidate_context("fraud_flags")
    invalidate_scope("detail")
    if recommendation_id:
        invalidate_entity("enforcement_recommendation", recommendation_id)


def invalidate_warm_context(context_key: str) -> None:
    """Used by warm cache command to target one context."""
    invalidate_context(context_key)
    agg = aggregate_id_for_context(context_key)
    invalidate_entity("national_risk", agg)
