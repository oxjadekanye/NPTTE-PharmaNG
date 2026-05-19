"""Phase 20B preparation — placeholder interfaces only (no OpenAI calls)."""
from __future__ import annotations


def copilot_summary_placeholder(*, entity_type: str, entity_id: str, context: dict | None = None) -> dict:
    return {
        "available": False,
        "phase": "20B",
        "message": "Copilot reasoning will attach here with policy grounding.",
        "entity_type": entity_type,
        "entity_id": entity_id,
    }


def investigative_suggestions_placeholder(*, bundle: dict) -> list[dict]:
    return [
        {"id": "review_timeline", "label": "Review custody timeline"},
        {"id": "escalate_enforcement", "label": "Consider enforcement escalation"},
    ]


def ministerial_briefing_placeholder(*, national_bundle: dict) -> str:
    return national_bundle.get("executive_summary") or "Ministerial briefing — Phase 20B copilot."


def policy_grounding_placeholder(*, query: str) -> dict:
    return {"grounded": False, "query": query, "citations": []}
