"""Phase 11 — aggregated operational feed for safe polling (no WebSocket)."""
from __future__ import annotations

from django.utils import timezone

from apps.alerts.models import NationalAlert
from apps.operations.models import ActivityFeedEntry, OperationalTask
from apps.streambus.services.bus import OperationalEventBus


def _serialize_alert(row: NationalAlert) -> dict:
    return {
        "id": str(row.id),
        "kind": "recall_alert" if "recall" in (row.alert_type or "").lower() else "national_alert",
        "title": row.title,
        "summary": row.description or "",
        "severity": row.severity,
        "priority": row.risk_level or row.severity,
        "state": row.state,
        "created_at": row.created_at.isoformat(),
    }


def build_operational_feed(
    *,
    organisation_id: str | None = None,
    since_sequence: int = 0,
    channels: list[str] | None = None,
    limit: int = 40,
) -> dict:
    """Merge streambus, alerts, tasks, and activity into one polling payload."""
    channel_filter = set(channels or [])
    bus_events = OperationalEventBus.replay(
        organisation_id=organisation_id,
        since_sequence=since_sequence,
        limit=limit,
    )
    normalized_events = []
    for ev in bus_events:
        payload = ev.get("payload") if isinstance(ev.get("payload"), dict) else {}
        kind = str(ev.get("event_type") or payload.get("event_type") or "operational")
        if channel_filter and kind not in channel_filter and payload.get("stream_channel") not in channel_filter:
            continue
        normalized_events.append(
            {
                "id": ev.get("event_id") or ev.get("id"),
                "kind": kind,
                "title": payload.get("title") or kind.replace("_", " ").title(),
                "summary": payload.get("summary") or payload.get("message") or "",
                "severity": ev.get("severity") or payload.get("severity") or "INFO",
                "sequence_number": ev.get("sequence_number", 0),
                "created_at": ev.get("created_at") or timezone.now().isoformat(),
                "payload": payload,
            }
        )

    alerts_qs = NationalAlert.objects.all().order_by("-created_at")[:15]
    if organisation_id:
        alerts_qs = alerts_qs.filter(organisation_id=organisation_id)
    alerts = [_serialize_alert(a) for a in alerts_qs]

    tasks_qs = OperationalTask.objects.filter(
        task_status__in=(OperationalTask.STATUS_OPEN, OperationalTask.STATUS_IN_PROGRESS)
    ).order_by("due_at")[:20]
    if organisation_id:
        tasks_qs = tasks_qs.filter(organisation_id=organisation_id)
    tasks = [
        {
            "id": str(t.id),
            "kind": "operational_task",
            "title": t.title,
            "summary": t.description,
            "priority": t.priority,
            "due_at": t.due_at.isoformat() if t.due_at else None,
            "task_status": t.task_status,
            "escalation_status": t.escalation_status,
        }
        for t in tasks_qs
    ]

    feed_qs = ActivityFeedEntry.objects.all().order_by("-created_at")[:15]
    if organisation_id:
        feed_qs = feed_qs.filter(organisation_id=organisation_id)
    activity = [
        {
            "id": str(f.id),
            "kind": f.feed_type,
            "title": f.title,
            "summary": f.summary,
            "severity": f.severity,
            "created_at": f.created_at.isoformat(),
        }
        for f in feed_qs
    ]

    max_seq = max((e.get("sequence_number", 0) for e in normalized_events), default=since_sequence)

    return {
        "events": normalized_events,
        "alerts": alerts,
        "tasks": tasks,
        "activity": activity,
        "since_sequence": max_seq,
        "polled_at": timezone.now().isoformat(),
        "transport": "polling",
    }
