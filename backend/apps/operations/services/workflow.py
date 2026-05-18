"""Workflow timeline and regulator operational history."""
from __future__ import annotations

import uuid

from apps.operations.models import RegulatorOperationalHistory, WorkflowTimelineEntry
from apps.operations.services.activity import record_activity


def record_workflow_event(
    *,
    workflow_type: str,
    title: str,
    summary: str = "",
    organisation=None,
    actor=None,
    entity_type: str = "",
    entity_id: uuid.UUID | None = None,
    created_by=None,
    record_feed: bool = True,
) -> WorkflowTimelineEntry:
    entry = WorkflowTimelineEntry.objects.create(
        workflow_type=workflow_type,
        title=title,
        summary=summary,
        organisation=organisation,
        actor=actor,
        entity_type=entity_type,
        entity_id=entity_id,
        created_by=created_by or actor,
        metadata={"entity_type": entity_type, "entity_id": str(entity_id) if entity_id else None},
    )
    if record_feed:
        record_activity(
            feed_type=workflow_type,
            title=title,
            summary=summary,
            organisation=organisation,
            actor=actor,
            entity_type=entity_type,
            entity_id=entity_id,
            created_by=created_by or actor,
        )
    return entry


def record_regulator_action(
    *,
    action_type: str,
    summary: str,
    actor,
    organisation=None,
    entity_type: str = "",
    entity_id: uuid.UUID | None = None,
) -> RegulatorOperationalHistory:
    row = RegulatorOperationalHistory.objects.create(
        action_type=action_type,
        summary=summary,
        organisation=organisation,
        actor=actor,
        entity_type=entity_type,
        entity_id=entity_id,
        created_by=actor,
        is_immutable=True,
        metadata={"entity_type": entity_type, "entity_id": str(entity_id) if entity_id else None},
    )
    record_activity(
        feed_type="regulator_action",
        title=action_type.replace("_", " ").title(),
        summary=summary,
        organisation=organisation,
        actor=actor,
        visibility="regulator",
        entity_type=entity_type,
        entity_id=entity_id,
        created_by=actor,
    )
    return row
