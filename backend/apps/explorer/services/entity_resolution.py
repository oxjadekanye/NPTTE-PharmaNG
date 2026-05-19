"""Resolve explorer query parameters to canonical explorer targets."""
from __future__ import annotations

from apps.explorer.constants import AGGREGATE_IDS, ENTITY_TYPES
from apps.explorer.services.registry import DrillDownRegistry


def resolve_entity(*, entity_type: str, entity_id: str) -> dict:
    et = (entity_type or "").strip()
    eid = (entity_id or "").strip()
    valid_type = et in ENTITY_TYPES
    aggregate = eid in AGGREGATE_IDS
    return {
        "entity_type": et,
        "entity_id": eid,
        "valid_entity_type": valid_type,
        "is_aggregate": aggregate,
        "known_aggregate": aggregate,
        "urls": {
            "detail": f"/api/v1/explorer/detail/{et}/{eid}/",
            "related": f"/api/v1/explorer/related/{et}/{eid}/",
            "timeline": f"/api/v1/explorer/timeline/{et}/{eid}/",
            "evidence": f"/api/v1/explorer/evidence/{et}/{eid}/",
            "actions": f"/api/v1/explorer/actions/{et}/{eid}/",
            "risk_breakdown": f"/api/v1/explorer/risk-breakdown/{et}/{eid}/",
        },
    }


__all__ = ["resolve_entity", "DrillDownRegistry"]
