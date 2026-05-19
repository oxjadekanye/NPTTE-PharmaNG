"""Phase 20C — regional command center intelligence."""
from __future__ import annotations

from django.db.models import Q

from apps.command_orchestration.constants import REGIONS
from apps.enforcement.models import EnforcementCase
from apps.operations.models import OperationalTask
from apps.organisations.models import Organisation
from apps.scanning.models import ScanEvent


def _state_filter(states: list[str]) -> Q:
    return Q(state__in=states) | Q(city__in=states)


def build_regional_intelligence(region_key: str) -> dict | None:
    meta = REGIONS.get(region_key)
    if not meta:
        return None
    states = meta["states"]
    org_q = Organisation.objects.filter(_state_filter(states))
    org_count = org_q.count()
    open_cases = EnforcementCase.objects.filter(
        organisation__state__in=states,
        case_status__in=(
            EnforcementCase.STATUS_OPEN,
            EnforcementCase.STATUS_INVESTIGATING,
            EnforcementCase.STATUS_ESCALATED,
        ),
    ).count()
    suspicious = ScanEvent.objects.filter(
        organisation__state__in=states,
        outcome_label__in=("suspicious", "counterfeit", "invalid"),
    ).count()
    overdue_tasks = OperationalTask.objects.filter(
        organisation__state__in=states,
        task_status=OperationalTask.STATUS_OPEN,
        due_at__isnull=False,
    ).count()
    readiness = max(20, 100 - open_cases * 4 - suspicious // 2)
    return {
        "region_key": region_key,
        "label": meta["label"],
        "states": states,
        "organisation_count": org_count,
        "open_investigations": open_cases,
        "counterfeit_signals": suspicious,
        "shortage_pressure": min(100, suspicious // 3 + overdue_tasks),
        "recall_pressure": open_cases,
        "enforcement_readiness": readiness,
        "active_officers": EnforcementCase.objects.filter(organisation__state__in=states)
        .exclude(assigned_regulator_id=None)
        .values("assigned_regulator")
        .distinct()
        .count(),
        "overdue_tasks": overdue_tasks,
        "ai_summary_hint": (
            f"{meta['label']}: {open_cases} open investigations, {suspicious} suspicious scans, "
            f"readiness index {readiness}/100."
        ),
    }


def list_regions() -> list[dict]:
    return [
        {"key": key, "label": meta["label"], "states": meta["states"]}
        for key, meta in REGIONS.items()
    ]
