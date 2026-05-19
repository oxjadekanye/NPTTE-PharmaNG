"""Extract source record citations from explorer bundles."""
from __future__ import annotations

from typing import Any


def _record_list(bundle: dict) -> list[dict]:
    records = bundle.get("records") or bundle.get("record_preview") or bundle.get("top_records") or []
    if isinstance(records, dict):
        records = records.get("items") or []
    if not isinstance(records, list):
        return []
    return [r for r in records if isinstance(r, dict)]


def extract_source_records(
    bundle: dict,
    *,
    selected_record_ids: list[str] | None = None,
    limit: int = 12,
) -> list[dict]:
    rows = _record_list(bundle)
    if selected_record_ids:
        wanted = {str(x) for x in selected_record_ids}
        rows = [r for r in rows if str(r.get("id", "")) in wanted]
    out: list[dict] = []
    for r in rows[:limit]:
        out.append(
            {
                "id": r.get("id"),
                "entity_type": r.get("entity_type"),
                "title": r.get("title") or r.get("name"),
                "organisation": r.get("organisation"),
                "full_address": r.get("full_address") or r.get("address"),
                "state": r.get("state"),
                "severity": r.get("severity"),
                "status": r.get("status"),
            }
        )
    return out
