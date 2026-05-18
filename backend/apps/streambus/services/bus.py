"""Central operational event bus — publish, subscribe, replay."""
from __future__ import annotations

import uuid
from typing import Any, Optional

from django.utils import timezone

from apps.core.constants import EventCategory
from apps.core.redis_bus import publish_channel
from apps.events.services import EventStreamService
from apps.streambus.constants import CHANNEL_DB, CHANNEL_REDIS, CHANNEL_SSE, SEV_INFO, STATE_DELIVERED, STATE_PUBLISHED
from apps.streambus.models import EventBusSubscription, EventLifecycleLog
from apps.streambus.services.deferred import enqueue_deferred_task
from apps.streambus.services.escalation import maybe_escalate_event


def _map_category(event_type: str) -> str:
    if event_type.startswith("scan"):
        return EventCategory.FRAUD if "suspicious" in event_type else EventCategory.VERIFICATION
    if "recall" in event_type:
        return EventCategory.EMERGENCY
    if "onboarding" in event_type or "approval" in event_type:
        return EventCategory.SYSTEM
    if "notification" in event_type:
        return EventCategory.SYSTEM
    return EventCategory.SYSTEM


class OperationalEventBus:
    @staticmethod
    def publish(
        *,
        event_type: str,
        payload: dict[str, Any],
        organisation_id=None,
        severity: str = SEV_INFO,
        correlation_id: uuid.UUID | None = None,
        source: str = "platform",
    ) -> dict:
        return publish_operational_event(
            event_type=event_type,
            payload=payload,
            organisation_id=organisation_id,
            severity=severity,
            correlation_id=correlation_id,
            source=source,
        )

    @staticmethod
    def replay(
        *,
        organisation_id=None,
        since_sequence: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
    ) -> list[dict]:
        events = EventStreamService.consume_event(
            category=category,
            organisation_id=organisation_id,
            since_sequence=since_sequence,
            limit=limit,
        )
        for ev in events:
            EventLifecycleLog.objects.create(
                event_id=ev["event_id"],
                correlation_id=uuid.uuid4(),
                event_type=ev.get("event_type", "replay"),
                category=ev.get("category", EventCategory.SYSTEM),
                organisation_id=ev.get("organisation_id"),
                lifecycle_state="replayed",
                delivery_channel=CHANNEL_SSE,
                sequence_number=ev.get("sequence_number", 0),
            )
        return events

    @staticmethod
    def acknowledge(*, event_id: str, actor=None) -> bool:
        updated = EventLifecycleLog.objects.filter(event_id=event_id, acknowledged_at__isnull=True).update(
            acknowledged_at=timezone.now(),
            lifecycle_state="acknowledged",
        )
        return updated > 0


def publish_operational_event(
    *,
    event_type: str,
    payload: dict[str, Any],
    organisation_id=None,
    severity: str = SEV_INFO,
    correlation_id: uuid.UUID | None = None,
    source: str = "platform",
) -> dict:
    correlation_id = correlation_id or uuid.uuid4()
    category = _map_category(event_type)
    enriched = {
        **payload,
        "correlation_id": str(correlation_id),
        "source": source,
        "severity": severity,
        "event_type": event_type,
    }
    event = EventStreamService.publish_event(
        category=category,
        event_type=event_type,
        payload=enriched,
        organisation_id=organisation_id,
    )
    EventLifecycleLog.objects.create(
        event_id=event.event_id,
        correlation_id=correlation_id,
        event_type=event_type,
        category=category,
        organisation_id=organisation_id,
        severity=severity,
        lifecycle_state=STATE_PUBLISHED,
        delivery_channel=CHANNEL_DB,
        sequence_number=event.sequence_number,
    )
    bus_message = EventStreamService._serialize(event)
    publish_channel(f"nptte:bus:{'regulator' if not organisation_id else organisation_id}", bus_message)
    publish_channel("nptte:bus:national", bus_message)
    EventLifecycleLog.objects.create(
        event_id=event.event_id,
        correlation_id=correlation_id,
        event_type=event_type,
        category=category,
        organisation_id=organisation_id,
        severity=severity,
        lifecycle_state=STATE_DELIVERED,
        delivery_channel=CHANNEL_REDIS,
        sequence_number=event.sequence_number,
    )
    maybe_escalate_event(
        event_id=event.event_id,
        correlation_id=correlation_id,
        event_type=event_type,
        severity=severity,
        organisation_id=organisation_id,
        payload=enriched,
    )
    enqueue_deferred_task(
        task_name="streambus_fanout",
        payload={"event_id": event.event_id, "event_type": event_type},
    )
    return bus_message


def list_subscriptions(*, user=None, organisation_id=None) -> list[EventBusSubscription]:
    qs = EventBusSubscription.objects.filter(is_active=True)
    if user:
        qs = qs.filter(user=user)
    if organisation_id:
        qs = qs.filter(organisation_id=organisation_id)
    return list(qs[:50])
