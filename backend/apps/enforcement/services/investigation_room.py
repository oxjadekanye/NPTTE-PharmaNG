"""Phase 20C — collaborative investigation room."""
from __future__ import annotations

from apps.enforcement.models import (
    EnforcementCase,
    EnforcementTimelineEntry,
    InvestigationAssignment,
    InvestigationComment,
    InvestigationNote,
)
from apps.enforcement.services.cases import assign_case
from apps.streambus.services.bus import publish_operational_event


def build_investigation_room(case: EnforcementCase) -> dict:
    notes = [
        {
            "id": str(n.id),
            "body": n.body,
            "note_type": n.note_type,
            "evidence_status": n.evidence_status,
            "author": n.author.get_full_name() if n.author_id else "System",
            "created_at": n.created_at.isoformat(),
        }
        for n in case.investigation_notes.select_related("author").all()[:50]
    ]
    comments = [
        {
            "id": str(c.id),
            "body": c.body,
            "escalation_level": c.escalation_level,
            "author": c.author.get_full_name() if c.author_id else "System",
            "created_at": c.created_at.isoformat(),
        }
        for c in case.investigation_comments.select_related("author").all()[:50]
    ]
    assignments = [
        {
            "investigator": a.investigator.get_full_name() if a.investigator_id else "",
            "assigned_at": a.assigned_at.isoformat(),
            "notes": a.notes,
        }
        for a in case.assignments.select_related("investigator").all()[:10]
    ]
    timeline = [
        {
            "id": str(t.id),
            "entry_type": t.entry_type,
            "summary": t.summary,
            "created_at": t.created_at.isoformat(),
        }
        for t in case.timeline_entries.all()[:30]
    ]
    return {
        "case": {
            "id": str(case.id),
            "title": case.title,
            "case_reference": case.case_reference,
            "case_status": case.case_status,
            "severity": case.severity,
            "summary": case.summary,
        },
        "notes": notes,
        "comments": comments,
        "assignments": assignments,
        "timeline": timeline,
        "activity_feed": timeline + [
            {"entry_type": "note", "summary": n["body"][:120], "created_at": n["created_at"]} for n in notes[:10]
        ],
    }


def add_investigation_note(
    *,
    case: EnforcementCase,
    author,
    body: str,
    note_type: str = "general",
    evidence_status: str = "",
) -> InvestigationNote:
    note = InvestigationNote.objects.create(
        case=case,
        author=author,
        body=body,
        note_type=note_type,
        evidence_status=evidence_status,
    )
    EnforcementTimelineEntry.objects.create(
        case=case,
        entry_type="investigation_note",
        summary=body[:255],
        actor=author,
    )
    publish_operational_event(
        event_type="enforcement.investigation.note",
        payload={
            "case_id": str(case.id),
            "note_id": str(note.id),
            "stream_channel": "investigation",
            "explorer_entity_type": "enforcement_case",
            "explorer_entity_id": str(case.id),
        },
        severity="INFO",
    )
    return note


def add_investigation_comment(
    *,
    case: EnforcementCase,
    author,
    body: str,
    escalation_level: int = 0,
) -> InvestigationComment:
    comment = InvestigationComment.objects.create(
        case=case,
        author=author,
        body=body,
        escalation_level=escalation_level,
    )
    EnforcementTimelineEntry.objects.create(
        case=case,
        entry_type="investigation_comment",
        summary=body[:255],
        actor=author,
    )
    publish_operational_event(
        event_type="enforcement.investigation.comment",
        payload={
            "case_id": str(case.id),
            "comment_id": str(comment.id),
            "escalation_level": escalation_level,
            "stream_channel": "investigation",
        },
        severity="WARNING" if escalation_level else "INFO",
    )
    return comment


def transfer_assignment(*, case: EnforcementCase, investigator, actor, notes: str = "") -> InvestigationAssignment:
    assign_case(case=case, investigator=investigator, actor=actor, notes=notes)
    InvestigationAssignment.objects.create(case=case, investigator=investigator, notes=notes)
    publish_operational_event(
        event_type="enforcement.investigation.transfer",
        payload={
            "case_id": str(case.id),
            "investigator_id": str(investigator.pk),
            "stream_channel": "investigation",
        },
        severity="INFO",
    )
    return case.assignments.first()
