"""Phase 20C — command room snapshot aggregation."""
from __future__ import annotations

from apps.command_orchestration.services.geospatial import build_map_markers, cluster_markers
from apps.command_orchestration.services.regional import list_regions
from apps.enforcement.models import EnforcementCase, EnforcementTimelineEntry
from apps.operations.models import OperationalTask
from apps.streambus.services.bus import OperationalEventBus
from apps.streambus.services.telemetry import aggregate_telemetry


def build_command_room_snapshot(*, request) -> dict:
    events = OperationalEventBus.replay(limit=25)

    open_cases = list(
        EnforcementCase.objects.exclude(
            case_status__in=(EnforcementCase.STATUS_RESOLVED, EnforcementCase.STATUS_CLOSED)
        )
        .order_by("-updated_at")[:12]
        .values("id", "title", "case_status", "severity", "case_reference")
    )
    tasks = list(
        OperationalTask.objects.filter(
            task_status__in=(OperationalTask.STATUS_OPEN, OperationalTask.STATUS_IN_PROGRESS)
        )
        .order_by("due_at")[:15]
        .values("id", "title", "priority", "task_status", "due_at", "escalation_status")
    )
    timeline = list(
        EnforcementTimelineEntry.objects.order_by("-created_at")[:20].values(
            "id", "entry_type", "summary", "created_at"
        )
    )
    markers = cluster_markers(build_map_markers(layer="operational", limit=80)["markers"], cell_deg=0.4)
    try:
        telemetry = aggregate_telemetry(organisation=None, window_seconds=300)
        tele = {
            "scan_throughput": telemetry.scan_throughput,
            "event_throughput": telemetry.event_throughput,
            "suspicious_rate": float(telemetry.suspicious_rate),
        }
    except Exception:
        tele = {}

    return {
        "live_events": events,
        "open_cases": open_cases,
        "operational_tasks": tasks,
        "timeline": timeline,
        "map_markers": markers,
        "regions": list_regions(),
        "telemetry": tele,
        "national_readiness_index": max(40, 100 - len(open_cases) * 3),
    }
