"""Realtime-ready event stream — Redis/Kafka abstraction layer."""
from __future__ import annotations

import uuid
from typing import Any, Optional, Type

from django.db import transaction
from django.utils import timezone

from apps.core.constants import EventCategory
from apps.events.models import EmergencyEvent, EventStreamBase, FraudEvent, InventoryEvent, SystemEvent, VerificationEvent

_CATEGORY_MODEL: dict[str, Type[EventStreamBase]] = {
    EventCategory.SYSTEM: SystemEvent,
    EventCategory.VERIFICATION: VerificationEvent,
    EventCategory.INVENTORY: InventoryEvent,
    EventCategory.EMERGENCY: EmergencyEvent,
    EventCategory.FRAUD: FraudEvent,
}


class EventStreamService:
    _sequence = 0

    @classmethod
    def _next_sequence(cls) -> int:
        cls._sequence += 1
        latest = SystemEvent.objects.order_by("-sequence_number").values_list("sequence_number", flat=True).first()
        return max((latest or 0) + 1, cls._sequence)

    @staticmethod
    def publish_event(
        *,
        category: str,
        event_type: str,
        payload: dict[str, Any],
        organisation_id=None,
        extra_fields: Optional[dict] = None,
    ) -> EventStreamBase:
        model = _CATEGORY_MODEL.get(category, SystemEvent)
        seq = EventStreamService._next_sequence()
        event_id = f"evt-{uuid.uuid4().hex[:16]}"
        fields = {
            "event_id": event_id,
            "category": category,
            "event_type": event_type,
            "organisation_id": organisation_id,
            "payload": payload,
            "published_at": timezone.now(),
            "sequence_number": seq,
        }
        if extra_fields:
            fields.update(extra_fields)
        with transaction.atomic():
            event = model.objects.create(**fields)
        EventStreamService._broadcast(event)
        return event

    @staticmethod
    def consume_event(
        *,
        category: Optional[str] = None,
        organisation_id=None,
        since_sequence: int = 0,
        limit: int = 100,
    ) -> list[dict]:
        """Replay events for regulators or organisation-scoped consumers."""
        results = []
        models = [_CATEGORY_MODEL[category]] if category else list(_CATEGORY_MODEL.values())
        for model in models:
            qs = model.objects.filter(is_archived=False, sequence_number__gt=since_sequence)
            if organisation_id:
                qs = qs.filter(organisation_id=organisation_id)
            for e in qs.order_by("sequence_number")[:limit]:
                results.append(EventStreamService._serialize(e))
        results.sort(key=lambda x: x["sequence_number"])
        return results[:limit]

    @staticmethod
    def archive_event(*, event_id: str, category: str) -> bool:
        model = _CATEGORY_MODEL.get(category, SystemEvent)
        updated = model.objects.filter(event_id=event_id, is_archived=False).update(is_archived=True)
        return updated > 0

    @staticmethod
    def _serialize(event: EventStreamBase) -> dict:
        return {
            "event_id": event.event_id,
            "category": event.category,
            "event_type": event.event_type,
            "organisation_id": str(event.organisation_id) if event.organisation_id else None,
            "payload": event.payload,
            "published_at": event.published_at.isoformat(),
            "sequence_number": event.sequence_number,
        }

    @staticmethod
    def _broadcast(event: EventStreamBase) -> None:
        """Redis Pub/Sub hook — no-op when Redis unavailable."""
        from django.conf import settings

        if not getattr(settings, "REDIS_URL", ""):
            return
        try:
            import json

            from django.core.cache import cache

            channel = f"nptte:events:{event.category}"
            cache.client.get_client().publish(channel, json.dumps(EventStreamService._serialize(event)))
        except Exception:
            pass
