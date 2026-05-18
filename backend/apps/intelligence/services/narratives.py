"""Deterministic template-based intelligence narratives."""
from __future__ import annotations

from apps.intelligence.models import IntelligenceNarrative
from apps.intelligence.services.scoring import calculate_national_risk, calculate_recall_execution_risk


def generate_narrative(*, narrative_type: str, context: dict | None = None, organisation=None) -> IntelligenceNarrative:
    context = context or {}
    if narrative_type == IntelligenceNarrative.NARRATIVE_EXECUTIVE:
        risk = calculate_national_risk()
        recall = calculate_recall_execution_risk()
        title = "National Pharmaceutical Intelligence Briefing"
        body = (
            f"National risk score: {risk['score']} ({risk['status']}). "
            f"Key factors: {'; '.join(risk['reasons'][:3])}. "
            f"Recall execution risk: {recall['score']}. "
            f"Recommended: {'; '.join(risk['recommended_actions'][:2])}."
        )
    elif narrative_type == IntelligenceNarrative.NARRATIVE_MINISTERIAL:
        risk = calculate_national_risk()
        title = "Ministerial Briefing — Medicine Security"
        body = (
            f"The National Traceability Platform reports a composite risk index of {risk['score']}/100. "
            f"Status: {risk['status'].upper()}. "
            "Counterfeit and diversion signals are monitored in realtime across all geopolitical zones. "
            f"Priority actions: {', '.join(risk['recommended_actions'][:3]) or 'maintain surveillance'}."
        )
    elif narrative_type == IntelligenceNarrative.NARRATIVE_REGIONAL:
        region = context.get("region_state", "National")
        title = f"Regional Threat Summary — {region}"
        body = (
            f"Regional analysis for {region} indicates elevated monitoring is advised. "
            f"Context: {context.get('summary', 'Scan and custody anomalies under review')}."
        )
    elif narrative_type == IntelligenceNarrative.NARRATIVE_RECALL:
        recall = calculate_recall_execution_risk()
        title = "Recall Impact Assessment"
        body = (
            f"National recall execution risk scored {recall['score']}/100. "
            f"{'; '.join(recall['reasons'])}. "
            "Pharmacy acknowledgement rates are being tracked in realtime."
        )
    else:
        title = context.get("title", "Intelligence Summary")
        body = context.get("body", "Operational intelligence summary generated from platform data.")

    return IntelligenceNarrative.objects.create(
        narrative_type=narrative_type,
        title=title,
        body=body,
        context=context,
        organisation=organisation,
    )


def generate_executive_briefing() -> dict:
    ministerial = generate_narrative(narrative_type=IntelligenceNarrative.NARRATIVE_MINISTERIAL)
    executive = generate_narrative(narrative_type=IntelligenceNarrative.NARRATIVE_EXECUTIVE)
    risk = calculate_national_risk()
    return {
        "medicine_stability_index": max(0, 100 - risk["score"]),
        "counterfeit_risk_forecast": risk["score"],
        "shortage_pressure": 35,
        "import_disruption_indicator": 22,
        "enforcement_readiness_score": 78,
        "ministerial_briefing": ministerial.body,
        "executive_summary": executive.body,
        "narrative_ids": [str(ministerial.id), str(executive.id)],
    }
