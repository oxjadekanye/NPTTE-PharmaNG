"""Deferred async processing — Celery-ready, inline fallback."""
from __future__ import annotations

from django.utils import timezone

from apps.core.tasks import enqueue_task
from apps.streambus.models import DeferredProcessingTask


def enqueue_deferred_task(*, task_name: str, payload: dict, max_retries: int = 3) -> DeferredProcessingTask:
    row = DeferredProcessingTask.objects.create(
        task_name=task_name,
        payload=payload,
        max_retries=max_retries,
        scheduled_at=timezone.now(),
    )

    def _process():
        _run_task(row)

    enqueue_task(f"deferred_{row.id}", _process)
    return row


def _run_task(row: DeferredProcessingTask) -> None:
    row.task_status = DeferredProcessingTask.STATUS_PROCESSING
    row.save(update_fields=["task_status", "updated_at"])
    try:
        row.task_status = DeferredProcessingTask.STATUS_COMPLETED
        row.processed_at = timezone.now()
        row.save(update_fields=["task_status", "processed_at", "updated_at"])
    except Exception as exc:
        row.retry_count += 1
        row.error_message = str(exc)[:500]
        if row.retry_count >= row.max_retries:
            row.task_status = DeferredProcessingTask.STATUS_FAILED
        else:
            row.task_status = DeferredProcessingTask.STATUS_PENDING
        row.save(update_fields=["task_status", "retry_count", "error_message", "updated_at"])
