"""Persistent activity feed recording."""
from __future__ import annotations

import uuid

from apps.operations.models import ActivityFeedEntry


def record_activity(
    *,
    feed_type: str,
    title: str,
    summary: str = "",
    organisation=None,
    actor=None,
    visibility: str = ActivityFeedEntry.VIS_ORGANISATION,
    severity: str = "INFO",
    entity_type: str = "",
    entity_id: uuid.UUID | None = None,
    created_by=None,
) -> ActivityFeedEntry:
    return ActivityFeedEntry.objects.create(
        feed_type=feed_type,
        title=title,
        summary=summary,
        organisation=organisation,
        actor=actor,
        visibility=visibility,
        severity=severity,
        entity_type=entity_type,
        entity_id=entity_id,
        created_by=created_by or actor,
    )
