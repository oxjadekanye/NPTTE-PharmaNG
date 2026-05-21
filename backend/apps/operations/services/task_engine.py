"""Phase 11 — field operations task engine (assign, escalate, notes, audit)."""
from __future__ import annotations

import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.operations.models import OperationalTask, RegulatorOperationalHistory
from apps.operations.services.activity import record_activity
from apps.operations.services.tasks import complete_task, create_operational_task
from apps.streambus.services.bus import publish_operational_event

User = get_user_model()


def serialize_task(task: OperationalTask) -> dict:
    return {
        "id": str(task.id),
        "title": task.title,
        "description": task.description,
        "task_type": task.task_type,
        "task_status": task.task_status,
        "priority": task.priority,
        "due_at": task.due_at.isoformat() if task.due_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        "escalation_status": task.escalation_status,
        "organisation_id": str(task.organisation_id) if task.organisation_id else None,
        "assigned_to": task.assigned_to.username if task.assigned_to else None,
        "assigned_to_id": str(task.assigned_to_id) if task.assigned_to_id else None,
        "related_entity_type": task.related_entity_type,
        "related_entity_id": str(task.related_entity_id) if task.related_entity_id else None,
        "operational_notes": task.operational_notes or [],
        "evidence_refs": task.evidence_refs or [],
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
    }


def assign_task(*, task: OperationalTask, assignee, actor=None) -> OperationalTask:
    task.assigned_to = assignee
    task.task_status = OperationalTask.STATUS_IN_PROGRESS
    task.save(update_fields=["assigned_to", "task_status", "updated_at"])
    _audit(actor, task, "Task assigned", f"Assigned to {assignee.username}")
    publish_operational_event(
        event_type="task.assigned",
        payload={"task_id": str(task.id), "assignee": assignee.username},
        organisation_id=task.organisation_id,
    )
    return task


def escalate_task(*, task: OperationalTask, actor=None, reason: str = "") -> OperationalTask:
    task.escalation_status = OperationalTask.ESC_ESCALATED
    task.priority = "high" if task.priority != "critical" else task.priority
    if task.priority == "normal":
        task.priority = "high"
    task.save(update_fields=["escalation_status", "priority", "updated_at"])
    _audit(actor, task, "Task escalated", reason or task.title)
    publish_operational_event(
        event_type="task.escalated",
        payload={"task_id": str(task.id), "reason": reason},
        organisation_id=task.organisation_id,
        severity="WARNING",
    )
    record_activity(
        feed_type="task_escalation",
        title=f"Escalated: {task.title}",
        summary=reason,
        organisation=task.organisation,
        actor=actor,
        severity="WARNING",
        created_by=actor,
    )
    return task


def append_task_note(*, task: OperationalTask, text: str, actor=None) -> OperationalTask:
    notes = list(task.operational_notes or [])
    notes.append(
        {
            "text": text,
            "author": actor.username if actor else "system",
            "at": timezone.now().isoformat(),
        }
    )
    task.operational_notes = notes[-50:]
    task.save(update_fields=["operational_notes", "updated_at"])
    return task


def attach_evidence_ref(*, task: OperationalTask, evidence_id: str, label: str = "") -> OperationalTask:
    refs = list(task.evidence_refs or [])
    refs.append({"evidence_id": evidence_id, "label": label or evidence_id})
    task.evidence_refs = refs[-30:]
    task.save(update_fields=["evidence_refs", "updated_at"])
    return task


def finish_task(*, task: OperationalTask, actor=None) -> OperationalTask:
    task = complete_task(task=task, actor=actor)
    task.completed_at = timezone.now()
    task.save(update_fields=["completed_at"])
    _audit(actor, task, "Task completed", task.title)
    return task


def overdue_tasks(*, organisation_id=None) -> list[OperationalTask]:
    qs = OperationalTask.objects.filter(
        task_status__in=(OperationalTask.STATUS_OPEN, OperationalTask.STATUS_IN_PROGRESS),
        due_at__lt=timezone.now(),
    )
    if organisation_id:
        qs = qs.filter(organisation_id=organisation_id)
    return list(qs.order_by("due_at")[:100])


def calendar_tasks(*, organisation_id=None, days: int = 30) -> list[dict]:
    end = timezone.now() + timedelta(days=days)
    qs = OperationalTask.objects.filter(due_at__lte=end).exclude(task_status=OperationalTask.STATUS_CANCELLED)
    if organisation_id:
        qs = qs.filter(organisation_id=organisation_id)
    return [
        {
            "id": str(t.id),
            "title": t.title,
            "due_at": t.due_at.isoformat() if t.due_at else None,
            "task_status": t.task_status,
            "priority": t.priority,
        }
        for t in qs.order_by("due_at")[:200]
    ]


def _audit(actor, task: OperationalTask, action: str, summary: str) -> None:
    if not actor:
        return
    RegulatorOperationalHistory.objects.create(
        action_type=RegulatorOperationalHistory.ACTION_ESCALATION
        if "escalat" in action.lower()
        else RegulatorOperationalHistory.ACTION_INVESTIGATION,
        organisation=task.organisation,
        actor=actor,
        summary=f"{action}: {summary}",
        entity_type="operational_task",
        entity_id=task.id,
    )


__all__ = [
    "assign_task",
    "append_task_note",
    "attach_evidence_ref",
    "calendar_tasks",
    "create_operational_task",
    "escalate_task",
    "finish_task",
    "overdue_tasks",
    "serialize_task",
]
