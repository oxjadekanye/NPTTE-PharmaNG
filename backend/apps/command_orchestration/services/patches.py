"""Phase 20C — patch envelopes for incremental realtime UI updates."""
from __future__ import annotations

from typing import Any


def build_event_patch(*, event_type: str, payload: dict) -> dict | None:
    """Return a patch envelope suitable for SSE `type: patch` messages."""
    et = (event_type or "").lower()
    entity_type = payload.get("explorer_entity_type") or payload.get("entity_type")
    entity_id = payload.get("explorer_entity_id") or payload.get("entity_id")
    context_key = payload.get("context_key") or payload.get("explorer_target", {}).get("context_key")

    if et.startswith("task."):
        return {
            "scope": "entity",
            "target": f"task:{payload.get('task_id') or entity_id}",
            "ops": {
                "task_status": payload.get("task_status"),
                "priority": payload.get("priority"),
                "escalation_status": payload.get("escalation_status"),
            },
        }

    if et.startswith("explorer.") or "explorer" in et:
        if context_key:
            return {
                "scope": "context",
                "target": str(context_key),
                "ops": {"invalidate": True, "reason": event_type},
            }
        if entity_type and entity_id:
            return {
                "scope": "entity",
                "target": f"{entity_type}:{entity_id}",
                "ops": {"invalidate": True, "reason": event_type},
            }

    if et.startswith("enforcement.") or "enforcement" in et:
        case_id = payload.get("case_id") or entity_id
        if case_id:
            return {
                "scope": "investigation",
                "target": str(case_id),
                "ops": {
                    "case_status": payload.get("case_status"),
                    "append_timeline": payload.get("summary"),
                },
            }

    if et.startswith("scan.") or "scan" in et:
        return {
            "scope": "metric",
            "target": "national_threat",
            "ops": {"delta_suspicious": 1, "last_event": event_type},
        }

    if et.startswith("recall."):
        return {
            "scope": "context",
            "target": "active_recalls",
            "ops": {"invalidate": True},
        }

    channel = payload.get("stream_channel")
    if channel:
        return {
            "scope": "channel",
            "target": str(channel),
            "ops": {"event_type": event_type, "severity": payload.get("severity")},
        }
    return None


def merge_patch_into_snapshot(snapshot: dict, patch: dict) -> dict:
    """Server-side helper for tests — shallow merge for metric patches."""
    if patch.get("scope") != "metric":
        return snapshot
    target = patch.get("target")
    ops = patch.get("ops") or {}
    metrics = dict(snapshot.get("metrics") or {})
    row = dict(metrics.get(target) or {})
    row.update(ops)
    metrics[target] = row
    return {**snapshot, "metrics": metrics}
