"""Phase 12 — scan ingestion and role-specific outcomes."""
from __future__ import annotations

from decimal import Decimal

from django.utils.dateparse import parse_datetime

from apps.ai_engine.services import calculate_counterfeit_probability
from apps.scanning.models import ScanEvent
from apps.serialization.gs1 import resolve_serial_from_scan
from apps.serialization.operations import record_serial_scan
from apps.verification.services import sovereign_verify


ROLE_OUTCOMES = {
    ScanEvent.SCAN_CITIZEN: {
        "authentic": "AUTHENTIC",
        "suspicious": "SUSPICIOUS",
        "recalled": "RECALLED",
        "expired": "EXPIRED",
        "duplicate_scan": "DUPLICATE_SCAN",
        "invalid_serial": "INVALID",
    },
    ScanEvent.SCAN_PHARMACY_RECEIVE: {
        "authentic": "received",
        "suspicious": "quarantined",
        "recalled": "quarantined",
        "expired": "quarantined",
        "default": "received",
    },
    ScanEvent.SCAN_PHARMACY_DISPENSE: {
        "authentic": "dispensed",
        "suspicious": "quarantined",
        "default": "dispensed",
    },
    ScanEvent.SCAN_REGULATOR: {
        "authentic": "inspection_passed",
        "suspicious": "flagged",
        "recalled": "seized",
        "default": "flagged",
    },
    ScanEvent.SCAN_CUSTOMS: {
        "authentic": "import_verified",
        "suspicious": "suspicious",
        "recalled": "held",
        "default": "held",
    },
    ScanEvent.SCAN_WAREHOUSE: {
        "authentic": "received",
        "suspicious": "temperature_breach",
        "default": "transferred",
    },
}


def _map_outcome(scan_type: str, verify_data: dict) -> str:
    outcome = (verify_data.get("outcome") or "").lower()
    bucket = verify_data.get("result") or ""
    mapping = ROLE_OUTCOMES.get(scan_type, {})
    if "recall" in outcome or bucket == "recalled":
        return mapping.get("recalled", mapping.get("default", "unknown"))
    if "expired" in outcome:
        return mapping.get("expired", mapping.get("default", "unknown"))
    if "duplicate" in outcome:
        return mapping.get("duplicate_scan", mapping.get("default", "unknown"))
    if verify_data.get("is_authentic") or bucket == "authentic":
        return mapping.get("authentic", mapping.get("default", "unknown"))
    if "invalid" in outcome:
        return mapping.get("invalid_serial", mapping.get("default", "unknown"))
    return mapping.get("suspicious", mapping.get("default", "unknown"))


def ingest_scan_event(
    *,
    request,
    serial_number: str,
    scan_type: str,
    actor_role: str = "",
    organisation=None,
    device_id: str = "",
    latitude=None,
    longitude=None,
    offline_timestamp=None,
    sync_status: str = ScanEvent.SYNC_SYNCED,
    replay_nonce: str = "",
    user=None,
) -> ScanEvent:
    raw = serial_number.strip()
    resolved = resolve_serial_from_scan(raw)

    verify_result = None
    outcome_label = "queued"
    result_payload: dict = {}

    if sync_status != ScanEvent.SYNC_PENDING:
        verify_result = sovereign_verify(
            request=request,
            serial_number=resolved,
            latitude=latitude,
            longitude=longitude,
            device_id=device_id or None,
        )
        result_payload = verify_result.get("data", {})
        outcome_label = _map_outcome(scan_type, result_payload)
        record_serial_scan(
            raw_scan=raw,
            scan_source=scan_type.replace("_", " "),
            scanner_type="mobile_camera",
            outcome=result_payload.get("outcome", ""),
            device_fingerprint=device_id,
            replay_nonce=replay_nonce,
            latitude=latitude,
            longitude=longitude,
            actor=user,
        )

    risk = Decimal("0")
    if resolved and sync_status != ScanEvent.SYNC_PENDING:
        try:
            risk = calculate_counterfeit_probability(serial_number=resolved)
        except Exception:
            risk = Decimal("0")

    offline_dt = None
    if offline_timestamp:
        if isinstance(offline_timestamp, str):
            offline_dt = parse_datetime(offline_timestamp)
        else:
            offline_dt = offline_timestamp

    event = ScanEvent.objects.create(
        serial_number=resolved or raw,
        scan_type=scan_type,
        actor_role=actor_role,
        organisation=organisation,
        user=user or (request.user if getattr(request, "user", None) and request.user.is_authenticated else None),
        device_id=device_id,
        latitude=latitude,
        longitude=longitude,
        offline_timestamp=offline_dt,
        sync_status=sync_status,
        risk_score=risk,
        outcome_label=outcome_label,
        result_payload=result_payload,
        replay_nonce=replay_nonce,
        created_by=user or (request.user if getattr(request, "user", None) and request.user.is_authenticated else None),
    )
    try:
        from apps.streambus.constants import EVT_SCAN, EVT_SCAN_SUSPICIOUS, SEV_CRITICAL, SEV_INFO
        from apps.streambus.services.bus import publish_operational_event

        alerts = _alert_hooks(event)
        publish_operational_event(
            event_type=EVT_SCAN_SUSPICIOUS if alerts.get("suspicious_scan_alert") else EVT_SCAN,
            payload={
                "scan_id": str(event.id),
                "serial_number": event.serial_number,
                "outcome_label": event.outcome_label,
                "summary": f"Scan {event.scan_type}: {event.outcome_label}",
            },
            organisation_id=organisation.id if organisation else None,
            severity=SEV_CRITICAL if alerts.get("suspicious_scan_alert") else SEV_INFO,
        )
    except Exception:
        pass
    return event


def serialize_scan_event(event: ScanEvent) -> dict:
    return {
        "id": str(event.id),
        "serial_number": event.serial_number,
        "scan_type": event.scan_type,
        "actor_role": event.actor_role,
        "outcome_label": event.outcome_label,
        "sync_status": event.sync_status,
        "risk_score": float(event.risk_score),
        "created_at": event.created_at.isoformat(),
        "result": event.result_payload,
        "alerts": _alert_hooks(event),
    }


def _alert_hooks(event: ScanEvent) -> dict:
    alerts = {
        "recall_alert": False,
        "suspicious_scan_alert": False,
        "counterfeit_warning": False,
        "failed_sync_warning": event.sync_status == ScanEvent.SYNC_FAILED,
    }
    outcome = (event.outcome_label or "").lower()
    if "recall" in outcome or "seized" in outcome or "held" in outcome:
        alerts["recall_alert"] = True
    if "suspicious" in outcome or "flagged" in outcome or "quarantine" in outcome:
        alerts["suspicious_scan_alert"] = True
    if float(event.risk_score) >= 50:
        alerts["counterfeit_warning"] = True
    return alerts
