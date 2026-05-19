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
    records = context.get("records") or []
    if isinstance(records, dict):
        records = records.get("items") or []
    states = context.get("state_distribution") or {}
    top_state = next(iter(states.keys()), "Lagos")
    return {
        "available": True,
        "source": "deterministic",
        "summary": summary.get("body") or summary.get("title") or "Operational briefing",
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
        "urgency_level": summary.get("severity") or "high",
        "assigned_owner_suggestion": records[0].get("assigned_officer") if records else "Regional supervisor",
        "next_24h_priority": "Triage critical alerts and open enforcement cases in top two states",
        "confidence": 0.72,
        "disclaimer": "AI-assisted recommendation — requires human review",
        "source_records": [{"id": r.get("id"), "title": r.get("title")} for r in records[:8]],
    }


def generate_operational_briefing(*, explorer_bundle: dict) -> dict:
    """
    Generate context-grounded briefing. Uses OpenAI when OPENAI_API_KEY is set; else deterministic fallback.
    """
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        return _deterministic_briefing(context=explorer_bundle)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        safe = {
            "summary": explorer_bundle.get("summary"),
            "record_count": explorer_bundle.get("record_count"),
            "severity_distribution": explorer_bundle.get("severity_distribution"),
            "state_distribution": explorer_bundle.get("state_distribution"),
            "recommended_actions": explorer_bundle.get("recommended_actions"),
            "records_preview": (explorer_bundle.get("records") or [])[:12]
            if isinstance(explorer_bundle.get("records"), list)
            else (explorer_bundle.get("records") or {}).get("items", [])[:12],
        }
        prompt = (
            "You are a national pharmaceutical regulator copilot for Nigeria. "
            "Return JSON only with keys: summary, risk_reason, affected_states (array), "
            "affected_organisations (array), affected_products (array), recommended_actions (array), "
            "urgency_level, assigned_owner_suggestion, next_24h_priority. "
            f"Context: {json.dumps(safe)[:6000]}"
        )
        def _call_openai():
            return client.chat.completions.create(
                model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=800,
                timeout=OPENAI_BRIEFING_TIMEOUT_SEC,
            )

        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(_call_openai)
            resp = future.result(timeout=OPENAI_BRIEFING_TIMEOUT_SEC + 2)
        text = (resp.choices[0].message.content or "").strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        data = json.loads(text)
        data["available"] = True
        data["source"] = "openai"
        data["confidence"] = 0.85
        data["disclaimer"] = "AI-assisted recommendation — requires human review"
        data["source_records"] = safe.get("records_preview", [])
        return data
    except (FuturesTimeout, Exception) as exc:
        logger.warning("OpenAI briefing failed, using fallback: %s", exc)
        out = _deterministic_briefing(context=explorer_bundle)
        out["source"] = "deterministic_fallback"
        return out
