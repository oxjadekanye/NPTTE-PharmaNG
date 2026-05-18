"""Streambus integration for enforcement events."""
from __future__ import annotations


def publish_enforcement_event(event_type: str, payload: dict) -> None:
    try:
        from apps.streambus.services.bus import publish_operational_event

        publish_operational_event(
            event_type=event_type,
            payload=payload,
            organisation_id=payload.get("organisation_id"),
            severity="CRITICAL" if "escalated" in event_type else "WARNING",
        )
    except Exception:
        pass
