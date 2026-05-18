"""Automated enforcement when intelligence risk crosses thresholds."""
from __future__ import annotations

from apps.enforcement.models import EnforcementCase, EnforcementRecommendation
from apps.enforcement.services.cases import create_enforcement_case
from apps.enforcement.services.events import publish_enforcement_event
from apps.enforcement.services.recommendations import create_recommendation
from apps.operations.services.activity import record_activity
from apps.operations.services.tasks import create_operational_task


def process_risk_threshold(
    *,
    risk_result: dict,
    organisation=None,
    context: str = "national",
    actor=None,
) -> dict:
    score = risk_result.get("score", 0)
    status = risk_result.get("status", "green")
    created = {"recommendations": [], "case_id": None}

    if score < 65:
        return created

    rec_type = EnforcementRecommendation.REC_INSPECTION
    if status == "critical":
        rec_type = EnforcementRecommendation.REC_SUSPENSION
    elif "recall" in " ".join(risk_result.get("reasons", [])).lower():
        rec_type = EnforcementRecommendation.REC_RECALL_ESCALATION
    elif organisation:
        org_type_code = getattr(getattr(organisation, "organisation_type", None), "code", "") or ""
        if org_type_code == "pharmacy":
            rec_type = EnforcementRecommendation.REC_PHARMACY_REVIEW

    rec = create_recommendation(
        recommendation_type=rec_type,
        title=f"Automated recommendation ({context})",
        rationale="; ".join(risk_result.get("reasons", [])[:5]),
        severity="critical" if status == "critical" else "high",
        organisation=organisation,
        risk_score=score,
        actor=actor,
    )
    created["recommendations"].append(str(rec.id))

    if score >= 80:
        case = create_enforcement_case(
            title=f"High-risk enforcement case — {context}",
            summary=risk_result.get("reasons", [""])[0] if risk_result.get("reasons") else "",
            severity=EnforcementCase.SEV_CRITICAL if status == "critical" else EnforcementCase.SEV_HIGH,
            organisation=organisation,
            actor=actor,
        )
        rec.case = case
        rec.save(update_fields=["case", "updated_at"])
        created["case_id"] = str(case.id)
        publish_enforcement_event("enforcement.case.escalated", {"case_id": str(case.id)})

    create_operational_task(
        title=f"Review enforcement recommendation: {rec.title[:60]}",
        task_type="enforcement_review",
        organisation=organisation,
        priority="high" if score >= 80 else "normal",
        created_by=actor,
    )
    record_activity(
        feed_type="enforcement",
        title="Enforcement recommendation generated",
        summary=rec.rationale[:200],
        organisation=organisation,
        severity="CRITICAL" if status == "critical" else "WARNING",
        created_by=actor,
    )
    try:
        from apps.notifications.services.delivery import notify_organisation_admins

        if organisation and score >= 70:
            notify_organisation_admins(
                organisation=organisation,
                title="Regulatory enforcement review required",
                body=rec.rationale[:500],
                severity="WARNING",
                notification_type="regulator",
            )
    except Exception:
        pass

    publish_intelligence_risk_updated(score, status, organisation)
    return created


def publish_intelligence_risk_updated(score, status, organisation) -> None:
    try:
        from apps.intelligence.services.events import publish_intelligence_event

        publish_intelligence_event(
            "intelligence.risk.updated",
            {
                "score": score,
                "status": status,
                "organisation_id": str(organisation.id) if organisation else None,
            },
        )
    except Exception:
        pass
