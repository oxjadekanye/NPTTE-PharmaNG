"""Enforcement case lifecycle management."""
from __future__ import annotations

import uuid

from django.utils import timezone

from apps.enforcement.models import EnforcementCase, EnforcementTimelineEntry, InvestigationAssignment
from apps.enforcement.services.events import publish_enforcement_event


def create_enforcement_case(
    *,
    title: str,
    summary: str = "",
    severity: str = EnforcementCase.SEV_MEDIUM,
    organisation=None,
    intelligence_signal_id=None,
    actor=None,
) -> EnforcementCase:
    case = EnforcementCase.objects.create(
        case_reference=f"ENF-{uuid.uuid4().hex[:8].upper()}",
        title=title,
        summary=summary,
        severity=severity,
        organisation=organisation,
        intelligence_signal_id=intelligence_signal_id,
        created_by=actor,
    )
    EnforcementTimelineEntry.objects.create(
        case=case,
        entry_type="case_opened",
        summary=f"Case opened: {title}",
        actor=actor,
        created_by=actor,
    )
    publish_enforcement_event("enforcement.case.created", {"case_id": str(case.id), "reference": case.case_reference})
    return case


def assign_case(*, case: EnforcementCase, investigator, actor=None, notes: str = "") -> InvestigationAssignment:
    case.assigned_regulator = investigator
    case.case_status = EnforcementCase.STATUS_INVESTIGATING
    case.save(update_fields=["assigned_regulator", "case_status", "updated_at"])
    assignment = InvestigationAssignment.objects.create(
        case=case,
        investigator=investigator,
        notes=notes,
        created_by=actor,
    )
    EnforcementTimelineEntry.objects.create(
        case=case,
        entry_type="assigned",
        summary=f"Assigned to {investigator.username}",
        actor=actor,
        created_by=actor,
    )
    return assignment
