"""Phase 20B — copilot reasoning orchestration with deterministic fallback."""
from __future__ import annotations

import json
from typing import Any

from apps.copilot.constants import DISCLAIMER, HUMAN_REVIEW_REQUIRED, PROMPT_MODES
from apps.copilot.services.cache import copilot_cache_key, get_cached_copilot, set_cached_copilot
from apps.copilot.services.context_loader import load_explorer_bundle, resolve_copilot_target
from apps.copilot.services.provider import call_openai_json, openai_available
from apps.copilot.services.sanitizer import sanitize_context, sanitize_user_question
from apps.copilot.services.source_records import extract_source_records


def _records(bundle: dict) -> list[dict]:
    from apps.copilot.services.source_records import _record_list

    return _record_list(bundle)


def _base_response(
    *,
    bundle: dict,
    mode: str,
    source: str,
    summary: str,
    reasoning: str,
    recommended_actions: list,
    urgency: str,
    confidence: float,
    selected_record_ids: list[str] | None = None,
) -> dict:
    return {
        "summary": summary,
        "reasoning": reasoning,
        "recommended_actions": recommended_actions,
        "urgency": urgency,
        "confidence": confidence,
        "source_records": extract_source_records(bundle, selected_record_ids=selected_record_ids),
        "human_review_required": HUMAN_REVIEW_REQUIRED,
        "disclaimer": DISCLAIMER,
        "source": source,
        "mode": mode,
        "entity_type": bundle.get("entity_type"),
        "entity_id": bundle.get("entity_id"),
    }


def _deterministic_explain_risk(bundle: dict) -> dict:
    summary = bundle.get("summary") or {}
    if isinstance(summary, dict):
        title = summary.get("title") or summary.get("body") or "Operational risk"
        body = summary.get("body") or ""
    else:
        title = str(summary)
        body = ""
    states = bundle.get("state_distribution") or {}
    reasons = (bundle.get("risk_explanation") or {}).get("reasons", [])
    if not reasons and bundle.get("severity_distribution"):
        reasons = [f"Severity mix: {bundle.get('severity_distribution')}"]
    reasoning = "; ".join(reasons[:5]) if reasons else f"Elevated indicators across {len(states) or 'multiple'} states."
    return _base_response(
        bundle=bundle,
        mode="explain_risk",
        source="deterministic",
        summary=title,
        reasoning=reasoning or body,
        recommended_actions=bundle.get("recommended_actions") or ["Review top severity records", "Assign field verification"],
        urgency=str(summary.get("severity") if isinstance(summary, dict) else bundle.get("risk_status") or "high"),
        confidence=0.72,
    )


def _deterministic_briefing(bundle: dict) -> dict:
    from apps.copilot.services.briefing import _deterministic_briefing as legacy

    leg = legacy(context=bundle)
    return _base_response(
        bundle=bundle,
        mode="generate_briefing",
        source=leg.get("source", "deterministic"),
        summary=leg.get("summary", ""),
        reasoning=leg.get("risk_reason", ""),
        recommended_actions=leg.get("recommended_actions", []),
        urgency=leg.get("urgency_level", "high"),
        confidence=float(leg.get("confidence", 0.72)),
    )


def _deterministic_recommend_actions(bundle: dict) -> dict:
    actions = bundle.get("recommended_actions") or []
    if not actions:
        for r in _records(bundle)[:3]:
            if r.get("recommended_action"):
                actions.append(str(r["recommended_action"]))
    if not actions:
        actions = [
            "Assign inspector within 24 hours",
            "Verify custody chain for flagged serials",
            "Escalate to enforcement if counterfeit confirmed",
        ]
    return _base_response(
        bundle=bundle,
        mode="recommend_actions",
        source="deterministic",
        summary="Recommended regulator actions",
        reasoning="Actions derived from operational records and national risk posture.",
        recommended_actions=actions[:8],
        urgency="high",
        confidence=0.7,
    )


def _deterministic_investigation(bundle: dict) -> dict:
    recs = _records(bundle)
    steps = [
        "Confirm organisation identity and site address against registry",
        "Pull custody timeline for linked serial numbers",
        "Cross-check batch approval status with NAFDAC records",
    ]
    if recs:
        r0 = recs[0]
        steps.insert(0, f"Interview accountable officer at {r0.get('organisation', 'flagged site')}")
    return _base_response(
        bundle=bundle,
        mode="summarise_investigation",
        source="deterministic",
        summary="Investigation summary",
        reasoning=" ".join(steps),
        recommended_actions=steps,
        urgency="medium",
        confidence=0.68,
    )


def _deterministic_enforcement_note(bundle: dict) -> dict:
    summary = bundle.get("summary") or {}
    title = summary.get("title") if isinstance(summary, dict) else str(summary)
    note = (
        f"Regulatory note — {title}\n"
        "Based on operational intelligence review, further verification is required before formal enforcement. "
        "Inspecting officer to confirm findings on site and document chain-of-custody."
    )
    return _base_response(
        bundle=bundle,
        mode="draft_enforcement_note",
        source="deterministic",
        summary="Draft enforcement note",
        reasoning=note,
        recommended_actions=["Schedule inspection", "Attach evidence exhibits", "Supervisor sign-off"],
        urgency="medium",
        confidence=0.65,
    )


def _deterministic_executive(bundle: dict) -> dict:
    leg = _deterministic_briefing(bundle)
    leg["mode"] = "executive_briefing"
    leg["summary"] = "National ministerial situational briefing"
    leg["reasoning"] = (
        f"{leg.get('reasoning', '')}\n\n"
        f"Next 24h priority: {bundle.get('next_24h_priority') or 'Triage critical alerts in top states'}"
    )
    return leg


def _deterministic_operational(bundle: dict, *, mode: str, title: str, reasoning: str, actions: list[str]) -> dict:
    return _base_response(
        bundle=bundle,
        mode=mode,
        source="deterministic",
        summary=title,
        reasoning=reasoning,
        recommended_actions=actions,
        urgency="high",
        confidence=0.71,
    )


def _deterministic_hotspot(bundle: dict) -> dict:
    states = list((bundle.get("state_distribution") or {}).keys())[:5]
    return _deterministic_operational(
        bundle,
        mode="hotspot_prediction",
        title="Predicted counterfeit hotspots",
        reasoning=f"Elevated scan anomalies concentrated in: {', '.join(states) or 'Lagos, Kano, Rivers'}.",
        actions=["Deploy field teams to top 3 states", "Increase customs screening at Apapa corridor"],
    )


def _deterministic_recall_spread(bundle: dict) -> dict:
    return _deterministic_operational(
        bundle,
        mode="recall_spread_analysis",
        title="Recall spread analysis",
        reasoning="Recall pressure likely to propagate via distributor hubs within 48–72 hours.",
        actions=["Notify regional supervisors", "Hold affected batches at wholesale nodes"],
    )


def _deterministic_shortage_forecast(bundle: dict) -> dict:
    return _deterministic_operational(
        bundle,
        mode="shortage_forecast",
        title="Shortage forecast",
        reasoning="Cold-chain and antimalarial categories show elevated shortage risk in northern corridors.",
        actions=["Release strategic buffer stock", "Monitor pharmacy dispensing rates"],
    )


def _deterministic_deployment(bundle: dict) -> dict:
    return _deterministic_operational(
        bundle,
        mode="deployment_suggestions",
        title="Officer deployment suggestions",
        reasoning="Rebalance inspectors toward highest severity open cases and overdue tasks.",
        actions=["Assign 2 inspectors to Lagos corridor", "Escalate overdue tasks >24h"],
    )


def _deterministic_escalation_reasoning(bundle: dict) -> dict:
    return _deterministic_operational(
        bundle,
        mode="escalation_reasoning",
        title="Escalation reasoning",
        reasoning="Combined counterfeit signals and open enforcement cases exceed regional tolerance.",
        actions=["Escalate to national enforcement desk", "Request ministerial situational note"],
    )


def _deterministic_operational_recommendations(bundle: dict) -> dict:
    leg = _deterministic_recommend_actions(bundle)
    leg["mode"] = "operational_recommendations"
    leg["summary"] = "AI operational coordination recommendations"
    return leg


_DETERMINISTIC = {
    "explain_risk": _deterministic_explain_risk,
    "generate_briefing": _deterministic_briefing,
    "recommend_actions": _deterministic_recommend_actions,
    "summarise_investigation": _deterministic_investigation,
    "draft_enforcement_note": _deterministic_enforcement_note,
    "executive_briefing": _deterministic_executive,
    "operational_recommendations": _deterministic_operational_recommendations,
    "escalation_reasoning": _deterministic_escalation_reasoning,
    "deployment_suggestions": _deterministic_deployment,
    "hotspot_prediction": _deterministic_hotspot,
    "recall_spread_analysis": _deterministic_recall_spread,
    "shortage_forecast": _deterministic_shortage_forecast,
}


def run_copilot_reasoning(
    *,
    request,
    mode: str,
    entity_type: str | None = None,
    entity_id: str | None = None,
    context_key: str | None = None,
    selected_record_ids: list[str] | None = None,
    user_question: str | None = None,
    use_cache: bool = True,
) -> tuple[dict | None, str]:
    """
    Returns (payload, error_reason).
    payload is None if access denied.
    """
    if mode not in PROMPT_MODES:
        return None, "invalid_mode"

    ok, reason, et, eid = resolve_copilot_target(
        request=request,
        entity_type=entity_type,
        entity_id=entity_id,
        context_key=context_key,
    )
    if not ok:
        return None, reason

    uid = str(request.user.pk) if request.user.is_authenticated else "anon"
    cache_key = copilot_cache_key(
        mode=mode,
        entity_type=et,
        entity_id=eid,
        context_key=context_key or "",
        selected_ids=selected_record_ids,
        user_id=uid,
    )
    if use_cache:
        hit = get_cached_copilot(cache_key)
        if hit:
            hit = {**hit, "cached": True}
            return hit, ""

    bundle = load_explorer_bundle(
        request=request,
        entity_type=et,
        entity_id=eid,
        context_key=context_key,
        selected_record_ids=selected_record_ids,
    )
    safe = sanitize_context(bundle)
    question = sanitize_user_question(user_question)

    fn = _DETERMINISTIC.get(mode, _deterministic_explain_risk)
    fallback = fn(bundle)

    ai_data = None
    if openai_available():
        system = (
            "You are NPTTE PharmaNG sovereign regulator copilot. "
            "Respond ONLY with valid JSON keys: summary, reasoning, recommended_actions (array of strings), "
            "urgency (low|medium|high|critical), confidence (0-1). "
            "Ground answers ONLY in provided context. Never invent organisations or addresses."
        )
        prompt = {
            "mode": mode,
            "context": safe,
            "user_question": question,
        }
        ai_data = call_openai_json(system=system, user_prompt=json.dumps(prompt)[:14000])

    if ai_data:
        out = _base_response(
            bundle=bundle,
            mode=mode,
            source="openai",
            summary=str(ai_data.get("summary") or fallback["summary"]),
            reasoning=str(ai_data.get("reasoning") or fallback["reasoning"]),
            recommended_actions=ai_data.get("recommended_actions") or fallback["recommended_actions"],
            urgency=str(ai_data.get("urgency") or fallback["urgency"]),
            confidence=float(ai_data.get("confidence", 0.85)),
            selected_record_ids=selected_record_ids,
        )
    else:
        out = {**fallback, "source": "deterministic_fallback" if openai_available() else fallback.get("source", "deterministic")}

    if use_cache:
        set_cached_copilot(cache_key, out)
    return out, ""
