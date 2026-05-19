"""Phase 20A — cache invalidation hooks."""
from __future__ import annotations

from apps.explorer.services.cache import invalidate_entity, invalidate_national, invalidate_scope


def on_streambus_event(*, event_type: str, payload: dict | None = None) -> None:
    payload = payload or {}
    invalidate_national()
    et = payload.get("explorer_entity_type")
    eid = payload.get("explorer_entity_id")
    if et and eid:
        invalidate_entity(str(et), str(eid))
    if event_type.startswith("enforcement."):
        invalidate_scope("detail")
        invalidate_scope("timeline")


def on_enforcement_mutation(*, entity_type: str = "enforcement_case", entity_id: str | None = None) -> None:
    invalidate_scope("detail")
    invalidate_scope("timeline")
    invalidate_scope("overview")
    if entity_id:
        invalidate_entity(entity_type, str(entity_id))


def on_investigation_update(*, case_id: str | None = None) -> None:
    on_enforcement_mutation(entity_type="enforcement_case", entity_id=case_id)


def on_recommendation_change(*, recommendation_id: str | None = None) -> None:
    invalidate_scope("detail")
    if recommendation_id:
        invalidate_entity("enforcement_recommendation", recommendation_id)
