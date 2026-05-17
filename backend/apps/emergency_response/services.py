"""National emergency distribution operations."""
from __future__ import annotations

from django.utils import timezone

from apps.core.constants import AlertCategory, AlertSeverity, EmergencyMode, EventCategory
from apps.emergency_response.models import CrisisDistributionPlan, NationalEmergencyProtocol
from apps.events.services import EventStreamService


def activate_emergency_distribution_mode(
    *, protocol_code: str, title: str, actor=None, target_states: list = None
) -> NationalEmergencyProtocol:
    protocol, _ = NationalEmergencyProtocol.objects.update_or_create(
        protocol_code=protocol_code,
        defaults={
            "title": title,
            "mode": EmergencyMode.CRISIS,
            "activated_at": timezone.now(),
            "created_by": actor,
        },
    )
    CrisisDistributionPlan.objects.get_or_create(
        protocol=protocol,
        plan_name=f"{protocol_code}-primary",
        defaults={"coverage_states": target_states or [], "created_by": actor},
    )
    from apps.alerts.services import create_national_alert

    create_national_alert(
        alert_type=AlertCategory.SHORTAGE,
        title=f"Emergency distribution activated: {title}",
        description=f"Protocol {protocol_code} — national crisis allocation mode.",
        severity=AlertSeverity.CRITICAL,
        risk_score=90,
    )
    EventStreamService.publish_event(
        category=EventCategory.EMERGENCY,
        event_type="emergency_distribution_activated",
        payload={"protocol_code": protocol_code, "states": target_states or []},
    )
    return protocol
