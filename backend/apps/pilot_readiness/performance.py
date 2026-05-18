"""Performance readiness indicators (Phase 11)."""
from __future__ import annotations

from apps.events.models import SystemEvent
from apps.serialization.models import ProductSerial
from apps.verification.models import VerificationScanLog


def build_performance_readiness() -> dict:
    serial_count = ProductSerial.objects.count()
    scan_count = VerificationScanLog.objects.count()
    event_count = SystemEvent.objects.count()

    return {
        "frontend_performance": {
            "status": "static_export_and_ssr_hybrid",
            "note": "Route-level code splitting on heavy map/chart routes.",
        },
        "backend_response": {
            "status": "rest_api_v1",
            "target_p95_ms": 500,
        },
        "database_growth": {
            "serials": serial_count,
            "scans": scan_count,
            "events": event_count,
            "readiness_note": "PostgreSQL indexed for serial_number, audit_reference, created_at.",
        },
        "event_volume_simulation": {
            "capacity_target_per_day": 500_000,
            "current_events": event_count,
        },
        "scan_volume_simulation": {
            "capacity_target_per_day": 1_000_000,
            "current_scans": scan_count,
        },
        "serial_volume_simulation": {
            "capacity_target": 10_000_000,
            "current_serials": serial_count,
        },
    }
