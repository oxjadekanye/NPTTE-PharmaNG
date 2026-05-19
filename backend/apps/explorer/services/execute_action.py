"""Execute explorer operational actions (additive, non-destructive by default)."""
from __future__ import annotations

import uuid

from apps.enforcement.models import EnforcementCase, EnforcementRecommendation
from apps.enforcement.services.cases import create_enforcement_case
from apps.enforcement.services.recommendations import dismiss_recommendation
from apps.intelligence.models import IntelligenceNarrative
from apps.intelligence.services.narratives import generate_narrative
from apps.operations.models import ActivityFeedEntry
from apps.operations.services.activity import record_activity
from apps.operations.services.tasks import create_operational_task
from apps.streambus.services.bus import publish_operational_event


def execute_explorer_action(
    *,
    request,
    entity_type: str,
    entity_id: str,
    action_id: str,
    payload: dict,
) -> dict:
    confirm = bool(payload.get("confirm"))
    user = request.user
    uid = None
    try:
        uid = uuid.UUID(str(entity_id))
    except (ValueError, TypeError):
        pass

    if action_id == "create_task":
        if not confirm:
            return {"ok": False, "error": "confirmation_required"}
        title = payload.get("title") or f"Explorer task — {entity_type}"
        org = None
        oid = payload.get("organisation_id")
        if oid:
            from apps.organisations.models import Organisation

            org = Organisation.objects.filter(pk=oid).first()
        task = create_operational_task(
            title=title[:255],
            task_type=payload.get("task_type") or "explorer_follow_up",
            organisation=org,
            description=payload.get("description", "")[:2000],
            priority=payload.get("priority") or "normal",
            related_entity_type=entity_type,
            related_entity_id=uid,
            created_by=user,
        )
        publish_operational_event(
            event_type="explorer.action.executed",
            payload={"action": action_id, "task_id": str(task.id), "entity_type": entity_type},
            organisation_id=org.id if org else None,
            severity="INFO",
        )
        return {"ok": True, "task_id": str(task.id)}

    if action_id == "record_acknowledgement":
        record_activity(
            feed_type="explorer",
            title="Explorer acknowledgement",
            summary=f"Acknowledged {entity_type}/{entity_id}",
            actor=user,
            created_by=user,
            entity_type=entity_type,
            entity_id=uid,
            visibility=ActivityFeedEntry.VIS_NATIONAL,
        )
        return {"ok": True}

    if action_id == "generate_briefing":
        n = generate_narrative(
            narrative_type=IntelligenceNarrative.NARRATIVE_EXECUTIVE,
            context={"source": "explorer", "entity_type": entity_type, "entity_id": entity_id},
        )
        return {"ok": True, "narrative_id": str(n.id)}

    if action_id == "open_investigation":
        if not confirm:
            return {"ok": False, "error": "confirmation_required"}
        case = create_enforcement_case(
            title=payload.get("title") or f"Investigation — {entity_type}",
            summary=payload.get("summary", "")[:2000],
            severity=payload.get("severity") or EnforcementCase.SEV_MEDIUM,
            intelligence_signal_id=uid if entity_type == "intelligence_signal" else None,
            actor=user,
        )
        return {"ok": True, "case_id": str(case.id)}

    if action_id == "mark_false_positive":
        if not confirm or not uid or entity_type != "enforcement_recommendation":
            return {"ok": False, "error": "invalid_action_context"}
        rec = EnforcementRecommendation.objects.filter(pk=uid).first()
        if not rec:
            return {"ok": False, "error": "not_found"}
        dismiss_recommendation(recommendation=rec, actor=user)
        return {"ok": True, "recommendation_id": str(rec.id)}

    return {"ok": False, "error": "unknown_action"}
