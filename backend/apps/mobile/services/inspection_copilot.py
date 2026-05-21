"""Deterministic field inspection recommendations for mobile copilot."""
from __future__ import annotations

from apps.copilot.services.reasoning import _base_response


def deterministic_inspection_recommendation(ctx: dict) -> dict:
    score = int(ctx.get("compliance_score") or 0)
    failed = list(ctx.get("failed_items") or [])
    evidence_count = int(ctx.get("evidence_count") or 0)
    site_ok = bool(ctx.get("site_passed"))
    product_ok = bool(ctx.get("product_passed"))
    compliance_ok = bool(ctx.get("compliance_passed"))

    concerns: list[str] = []
    evidence_req: list[str] = []
    actions: list[str] = []
    urgency = "medium"
    escalation = False
    timeframe = "Within 7 days"

    if score < 40:
        urgency = "critical"
        escalation = True
        timeframe = "Within 24 hours"
        concerns.append("Compliance score below 40% — immediate regulatory response required.")
        actions.append("Suspend dispensing of flagged stock and open formal enforcement case")

    if not product_ok:
        concerns.append("Product verification incomplete — serial/batch integrity not confirmed.")
        actions.append("Quarantine affected lots and re-scan serial samples against NAFDAC registry")

    if not compliance_ok:
        concerns.append("Compliance documentation gaps — custody or recall acknowledgement missing.")
        actions.append("Issue corrective action notice and schedule mandatory re-inspection")

    failed_text = " ".join(failed).lower()
    if "cold-chain" in failed_text or "storage" in failed_text:
        concerns.append("Cold-chain or storage conditions failed.")
        actions.append("Urgent storage inspection — verify refrigeration logs within 12 hours")
        urgency = "critical"
        escalation = True

    if evidence_count < 1:
        concerns.append("No photographic evidence attached to this inspection.")
        evidence_req.extend(["Site photos", "Storage area photos", "Serial sample capture"])

    if not site_ok:
        concerns.append("Site verification incomplete.")

    if not concerns:
        concerns.append("Guided checklist substantially complete.")
        actions.append("Maintain custody documentation; routine spot-check within 30 days")
        urgency = "low"

    bundle = {
        "entity_type": "inspection",
        "summary": {"title": f"Field inspection — {score}% compliance", "severity": urgency},
        "recommended_actions": actions,
        "risk_explanation": {"reasons": concerns},
    }
    payload = _base_response(
        bundle=bundle,
        mode="operational_recommendations",
        source="deterministic_inspection",
        summary=f"Inspection risk: {urgency}",
        reasoning="; ".join(concerns[:6]),
        recommended_actions=actions[:6],
        urgency=urgency,
        confidence=0.82 if score >= 70 else 0.65,
    )
    payload["risk_rating"] = urgency
    payload["immediate_concerns"] = concerns
    payload["evidence_required"] = evidence_req or ["Officer signature on enforcement record"]
    payload["follow_up_timeframe"] = timeframe
    payload["escalation_required"] = escalation
    return payload
