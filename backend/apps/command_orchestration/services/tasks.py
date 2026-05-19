"""Phase 20C — live operational task orchestration."""
from __future__ import annotations

from django.utils import timezone

from apps.operations.models import OperationalTask


def build_task_orchestration_snapshot() -> dict:
    now = timezone.now()
    open_qs = OperationalTask.objects.filter(
        task_status__in=(OperationalTask.STATUS_OPEN, OperationalTask.STATUS_IN_PROGRESS)
    ).select_related("assigned_to", "organisation").order_by("due_at", "-created_at")[:40]

    tasks = []
    overdue = 0
    for t in open_qs:
        is_overdue = bool(t.due_at and t.due_at < now)
        if is_overdue:
            overdue += 1
        tasks.append(
            {
                "id": str(t.id),
                "title": t.title,
                "priority": t.priority,
                "task_status": t.task_status,
                "due_at": t.due_at.isoformat() if t.due_at else None,
                "escalation_status": t.escalation_status,
                "overdue": is_overdue,
                "assigned_to": t.assigned_to.get_full_name() if t.assigned_to_id else None,
                "organisation": t.organisation.legal_name if t.organisation_id else None,
                "sla_seconds_remaining": int((t.due_at - now).total_seconds()) if t.due_at and t.due_at > now else 0,
            }
        )

    by_region: dict[str, int] = {}
    for t in tasks:
        org_state = t.get("organisation") or "National"
        by_region[org_state] = by_region.get(org_state, 0) + 1

    return {
        "tasks": tasks,
        "overdue_count": overdue,
        "open_count": len(tasks),
        "regional_queue": by_region,
        "sla_indicator": max(0, 100 - overdue * 5),
    }
