"""Streambus integration for intelligence events."""
from __future__ import annotations


def publish_intelligence_event(event_type: str, payload: dict) -> None:
    try:
        from apps.streambus.services.bus import publish_operational_event

        publish_operational_event(
            event_type=event_type,
            payload=payload,
            organisation_id=payload.get("organisation_id"),
            severity="WARNING" if "cluster" in event_type or "signal" in event_type else "INFO",
        )
    except Exception:
        pass
