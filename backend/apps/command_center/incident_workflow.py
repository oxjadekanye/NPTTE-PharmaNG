"""Phase 10 — persistent incident escalation and assignment."""
from __future__ import annotations

from django.utils import timezone

from apps.command_center.models import NationalIncident
from apps.core.constants import IncidentStatus
from apps.events.services import EventStreamService
from apps.core.constants import EventCategory


def assign_investigator(*, incident: NationalIncident, investigator: str, actor=None) -> NationalIncident:
    incident.assigned_investigator = investigator
    incident.workflow_state = "investigating"
    incident.status = IncidentStatus.INVESTIGATING
    incident.save(update_fields=["assigned_investigator", "workflow_state", "status", "updated_at"])
    EventStreamService.publish_event(
        category=EventCategory.EMERGENCY,
        event_type="incident_assigned",
        payload={"incident_code": incident.incident_code, "investigator": investigator},
    )
    return incident


def escalate_incident(*, incident: NationalIncident, reason: str, national: bool = False) -> NationalIncident:
    incident.escalation_level = min(incident.escalation_level + 1, 5)
    incident.workflow_state = "national_emergency" if national else "escalated"
    if national:
        incident.status = IncidentStatus.INVESTIGATING
    evidence = list(incident.evidence_lifecycle or [])
    evidence.append({"at": timezone.now().isoformat(), "event": f"Escalation: {reason}"})
    incident.evidence_lifecycle = evidence
    incident.save(
        update_fields=["escalation_level", "workflow_state", "status", "evidence_lifecycle", "updated_at"]
    )
    EventStreamService.publish_event(
        category=EventCategory.EMERGENCY,
        event_type="incident_escalated",
        payload={"incident_code": incident.incident_code, "level": incident.escalation_level, "reason": reason},
    )
    return incident
