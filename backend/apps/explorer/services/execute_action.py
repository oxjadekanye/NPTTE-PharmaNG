"""Execute explorer operational actions (Phase 20A.2 practical workflows)."""
from __future__ import annotations

import uuid
from datetime import timedelta

from django.utils import timezone
from django.utils.dateparse import parse_datetime

from apps.alerts.models import NationalAlert, NationalAlertEscalation
from apps.enforcement.models import EnforcementCase, EnforcementRecommendation
from apps.enforcement.services.cases import assign_case, create_enforcement_case
from apps.enforcement.services.recommendations import dismiss_recommendation
from apps.explorer.services.payloads import build_explorer_bundle
from apps.operations.models import ActivityFeedEntry
from apps.operations.services.activity import record_activity
from apps.operations.services.tasks import create_operational_task
from apps.streambus.services.bus import publish_operational_event


def _parse_due(payload: dict):
    due_date = payload.get("due_date")
    due_time = payload.get("due_time")
    if due_date:
        text = str(due_date)
        if due_time:
            text = f"{due_date}T{due_time}"
        parsed = parse_datetime(text)
        if parsed:
            return timezone.make_aware(parsed) if timezone.is_naive(parsed) else parsed
    days = payload.get("due_in_days")
    if days is not None:
        try:
            return timezone.now() + timedelta(days=int(days))
        except (TypeError, ValueError):
            pass
    return None


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
        from django.contrib.auth import get_user_model

        User = get_user_model()
        assignee = None
        aid = payload.get("assigned_officer_id") or payload.get("assignee_id")
        if aid:
            assignee = User.objects.filter(pk=aid).first()
        org = None
        oid = payload.get("organisation_id")
        if oid:
            from apps.organisations.models import Organisation

            org = Organisation.objects.filter(pk=oid).first()
        due_at = _parse_due(payload)
        desc = payload.get("description", "")[:2000]
        checklist = payload.get("checklist")
        if checklist:
            desc = f"{desc}\n\nChecklist: {checklist}"[:2000]
        task = create_operational_task(
            title=(payload.get("title") or f"Explorer task — {entity_type}")[:255],
            task_type=payload.get("task_type") or "explorer_follow_up",
            organisation=org,
            assigned_to=assignee,
            description=desc,
            priority=payload.get("priority") or "normal",
            due_in_days=int(payload.get("due_in_days") or 7),
            related_entity_type=entity_type,
            related_entity_id=uid,
            created_by=user,
        )
        if due_at:
            task.due_at = due_at
            task.save(update_fields=["due_at", "updated_at"])
        publish_operational_event(
            event_type="explorer.action.executed",
            payload={
                "action": action_id,
                "task_id": str(task.id),
                "entity_type": entity_type,
                "explorer_entity_type": entity_type,
                "explorer_entity_id": entity_id,
            },
            organisation_id=org.id if org else None,
            severity="INFO",
        )
        return {"ok": True, "task_id": str(task.id), "message": "Operational task created"}

    if action_id == "record_acknowledgement":
        record_activity(
            feed_type="explorer",
            title="Explorer acknowledgement",
            summary=f"Acknowledged {entity_type}/{entity_id} by {user.username}",
            actor=user,
            created_by=user,
            entity_type=entity_type,
            entity_id=uid,
            visibility=ActivityFeedEntry.VIS_NATIONAL,
            severity="SUCCESS",
        )
        if entity_type == "alert" and uid:
            alert = NationalAlert.objects.filter(pk=uid).first()
            if alert:
                ev = alert.evidence_payload if isinstance(alert.evidence_payload, dict) else {}
                ev["reviewed_by"] = user.username
                ev["reviewed_at"] = timezone.now().isoformat()
                ev["action_status"] = "reviewed"
                alert.evidence_payload = ev
                alert.save(update_fields=["evidence_payload", "updated_at"])
        publish_operational_event(
            event_type="explorer.acknowledgement",
            payload={"entity_type": entity_type, "entity_id": entity_id, "explorer_entity_type": entity_type, "explorer_entity_id": entity_id},
            severity="INFO",
        )
        return {"ok": True, "message": "Acknowledgement recorded"}

    if action_id == "generate_briefing":
        from apps.explorer.constants import AGGREGATE_IDS
        from apps.explorer.services.context_summary import build_light_overview
        from apps.copilot.services.briefing import generate_operational_briefing

        if entity_id in AGGREGATE_IDS:
            bundle = build_light_overview(request, entity_type, entity_id)
            bundle["records"] = bundle.get("record_preview") or []
        else:
            bundle = build_explorer_bundle(request, entity_type, entity_id)
        briefing = generate_operational_briefing(explorer_bundle=bundle, request=request)
        return {"ok": True, "briefing": briefing, "message": "Briefing generated"}

    if action_id == "open_investigation":
        if not confirm:
            return {"ok": False, "error": "confirmation_required"}
        from django.contrib.auth import get_user_model

        User = get_user_model()
        investigator = None
        iid = payload.get("assigned_officer_id") or payload.get("investigator_id")
        if iid:
            investigator = User.objects.filter(pk=iid).first()
        case = create_enforcement_case(
            title=(payload.get("title") or f"Investigation — {entity_type}")[:255],
            summary=(payload.get("summary") or payload.get("rationale", ""))[:2000],
            severity=payload.get("severity") or EnforcementCase.SEV_MEDIUM,
            intelligence_signal_id=uid if entity_type == "intelligence_signal" else None,
            actor=user,
        )
        if investigator:
            assign_case(case=case, investigator=investigator, actor=user, notes=payload.get("notes", ""))
        publish_operational_event(
            event_type="enforcement.case.created",
            payload={
                "case_id": str(case.id),
                "explorer_entity_type": entity_type,
                "explorer_entity_id": entity_id,
            },
            severity="HIGH",
        )
        return {"ok": True, "case_id": str(case.id), "case_reference": case.case_reference, "message": "Investigation opened"}

    if action_id == "escalate_alert":
        if not confirm:
            return {"ok": False, "error": "confirmation_required"}
        if entity_type != "alert" or not uid:
            return {"ok": False, "error": "invalid_action_context"}
        alert = NationalAlert.objects.filter(pk=uid).first()
        if not alert:
            return {"ok": False, "error": "not_found"}
        level = int(payload.get("escalation_level") or alert.escalation_level + 1)
        alert.escalation_level = level
        ev = alert.evidence_payload if isinstance(alert.evidence_payload, dict) else {}
        ev["escalation_status"] = "escalated"
        ev["escalation_reason"] = payload.get("reason", "")[:500]
        alert.evidence_payload = ev
        alert.save(update_fields=["escalation_level", "evidence_payload", "updated_at"])
        NationalAlertEscalation.objects.create(
            alert=alert,
            escalated_to=payload.get("escalated_to", "National enforcement desk")[:128],
            notes=(payload.get("reason") or "Explorer escalation")[:2000],
            created_by=user,
        )
        publish_operational_event(
            event_type="alert.escalated",
            payload={"alert_id": str(alert.id), "level": level, "explorer_entity_type": "alert", "explorer_entity_id": entity_id},
            severity="HIGH",
        )
        return {"ok": True, "escalation_level": level, "message": "Alert escalated"}

    if action_id == "mark_false_positive":
        if not confirm or not uid or entity_type != "enforcement_recommendation":
            return {"ok": False, "error": "invalid_action_context"}
        rec = EnforcementRecommendation.objects.filter(pk=uid).first()
        if not rec:
            return {"ok": False, "error": "not_found"}
        dismiss_recommendation(recommendation=rec, actor=user)
        return {"ok": True, "recommendation_id": str(rec.id)}

    return {"ok": False, "error": "unknown_action"}
