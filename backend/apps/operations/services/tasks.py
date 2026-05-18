"""Operational task engine."""
from __future__ import annotations

import uuid
from datetime import timedelta

from django.utils import timezone

from apps.operations.models import OperationalTask
from apps.operations.services.activity import record_activity


def create_operational_task(
    *,
    title: str,
    task_type: str,
    organisation=None,
    assigned_to=None,
    description: str = "",
    priority: str = "normal",
    due_in_days: int | None = 7,
    related_entity_type: str = "",
    related_entity_id: uuid.UUID | None = None,
    created_by=None,
) -> OperationalTask:
    due_at = timezone.now() + timedelta(days=due_in_days) if due_in_days else None
    task = OperationalTask.objects.create(
        title=title,
        description=description,
        task_type=task_type,
        organisation=organisation,
        assigned_to=assigned_to,
        priority=priority,
        due_at=due_at,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
        created_by=created_by,
    )
    record_activity(
        feed_type="task",
        title=f"Task assigned: {title}",
        summary=description,
        organisation=organisation,
        actor=created_by,
        created_by=created_by,
    )
    return task


def complete_task(*, task: OperationalTask, actor=None) -> OperationalTask:
    task.task_status = OperationalTask.STATUS_COMPLETED
    task.save(update_fields=["task_status", "updated_at"])
    record_activity(
        feed_type="task",
        title=f"Task completed: {task.title}",
        organisation=task.organisation,
        actor=actor,
        severity="SUCCESS",
        created_by=actor,
    )
    return task
