"""Enforcement recommendations from intelligence thresholds."""
from __future__ import annotations

from apps.enforcement.models import EnforcementCase, EnforcementRecommendation, EnforcementTimelineEntry
from apps.enforcement.services.cases import create_enforcement_case
from apps.enforcement.services.events import publish_enforcement_event


def create_recommendation(
    *,
    recommendation_type: str,
    title: str,
    rationale: str,
    severity: str = "medium",
    organisation=None,
    risk_score: float = 0,
    case: EnforcementCase | None = None,
    actor=None,
) -> EnforcementRecommendation:
    rec = EnforcementRecommendation.objects.create(
        recommendation_type=recommendation_type,
        title=title,
        rationale=rationale,
        severity=severity,
        organisation=organisation,
        risk_score=risk_score,
        case=case,
        created_by=actor,
    )
    publish_enforcement_event(
        "enforcement.recommendation.created",
        {"recommendation_id": str(rec.id), "type": recommendation_type},
    )
    return rec


def accept_recommendation(*, recommendation: EnforcementRecommendation, actor=None) -> EnforcementRecommendation:
    recommendation.recommendation_status = EnforcementRecommendation.STATUS_ACCEPTED
    recommendation.save(update_fields=["recommendation_status", "updated_at"])
    if recommendation.case:
        EnforcementTimelineEntry.objects.create(
            case=recommendation.case,
            entry_type="recommendation_accepted",
            summary=f"Accepted: {recommendation.title}",
            actor=actor,
            created_by=actor,
        )
    return recommendation


def dismiss_recommendation(*, recommendation: EnforcementRecommendation, actor=None) -> EnforcementRecommendation:
    recommendation.recommendation_status = EnforcementRecommendation.STATUS_DISMISSED
    recommendation.save(update_fields=["recommendation_status", "updated_at"])
    return recommendation
