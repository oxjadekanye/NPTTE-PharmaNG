"""Phase 20A.2 — AI-assisted operational briefing (server-side only)."""
from __future__ import annotations

import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from typing import Any

OPENAI_BRIEFING_TIMEOUT_SEC = 12

logger = logging.getLogger("nptte.copilot.briefing")


def _deterministic_briefing(*, context: dict) -> dict:
    summary = context.get("summary") or {}
    if isinstance(summary, str):
        summary_title = summary
        summary_body = summary
        summary_severity = context.get("risk_status") or "high"
    elif isinstance(summary, dict):
        summary_title = summary.get("title") or "Operational briefing"
        summary_body = summary.get("body") or summary_title
        summary_severity = summary.get("severity") or context.get("risk_status") or "high"
    else:
        summary_title = "Operational briefing"
        summary_body = str(summary)
        summary_severity = context.get("risk_status") or "high"
    records = context.get("records") or []
    if isinstance(records, dict):
        records = records.get("items") or []
    states = context.get("state_distribution") or {}
    top_state = next(iter(states.keys()), "Lagos")
    return {
        "available": True,
        "source": "deterministic",
        "summary": summary_body or summary_title,
        "risk_reason": "; ".join((context.get("risk_explanation") or {}).get("reasons", [])[:3])
        or "Elevated national pharmaceutical risk indicators",
        "affected_states": list(states.keys())[:8] or [top_state],
        "affected_organisations": [r.get("organisation") for r in records[:5] if r.get("organisation")],
        "affected_products": [r.get("product") for r in records[:5] if r.get("product")],
        "recommended_actions": context.get("recommended_actions")
        or [
            "Assign field inspector within 24h",
            "Verify batch custody at flagged pharmacies",
            "Prepare ministerial situational update",
        ],
        "urgency_level": summary_severity,
        "assigned_owner_suggestion": records[0].get("assigned_officer") if records else "Regional supervisor",
        "next_24h_priority": "Triage critical alerts and open enforcement cases in top two states",
        "confidence": 0.72,
        "disclaimer": "AI-assisted recommendation — requires human review",
        "source_records": [{"id": r.get("id"), "title": r.get("title")} for r in records[:8]],
    }


def generate_operational_briefing(*, explorer_bundle: dict, request=None) -> dict:
    """
    Generate context-grounded briefing. Uses Phase 20B reasoning when request provided;
    otherwise legacy deterministic/OpenAI path for backward compatibility.
    """
    if request is not None:
        from apps.copilot.services.reasoning import run_copilot_reasoning

        payload, _reason = run_copilot_reasoning(
            request=request,
            mode="generate_briefing",
            entity_type=str(explorer_bundle.get("entity_type") or ""),
            entity_id=str(explorer_bundle.get("entity_id") or ""),
            context_key=str(explorer_bundle.get("context_key") or "") or None,
        )
        if payload:
            leg = _deterministic_briefing(context=explorer_bundle)
            leg.update(
                {
                    "available": True,
                    "summary": payload.get("summary"),
                    "risk_reason": payload.get("reasoning"),
                    "recommended_actions": payload.get("recommended_actions"),
                    "urgency_level": payload.get("urgency"),
                    "confidence": payload.get("confidence"),
                    "disclaimer": payload.get("disclaimer"),
                    "source_records": payload.get("source_records"),
                    "source": payload.get("source"),
                }
            )
            return leg

    return _deterministic_briefing(context=explorer_bundle)
