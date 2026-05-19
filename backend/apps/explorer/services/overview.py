"""Phase 20A — lightweight explorer overview payloads (fast drawer first paint)."""
from __future__ import annotations

from apps.explorer.services.context_summary import build_light_overview


def build_explorer_overview(request, entity_type: str, entity_id: str) -> dict:
    """Summary + metadata only — capped record preview."""
    return build_light_overview(request, entity_type, entity_id)
