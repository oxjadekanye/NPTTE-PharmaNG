"""Maps explorer entity types to resolution metadata (Phase 19 registry)."""
from __future__ import annotations

from apps.explorer.constants import AGGREGATE_IDS, ENTITY_TYPES


class DrillDownRegistry:
    """Declarative registry of supported drill-down entity types."""

    @staticmethod
    def is_known_entity_type(entity_type: str) -> bool:
        return entity_type in ENTITY_TYPES

    @staticmethod
    def is_aggregate(entity_id: str) -> bool:
        return entity_id in AGGREGATE_IDS
