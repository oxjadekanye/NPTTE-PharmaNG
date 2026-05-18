"""Phase 10 — scanner abstraction for camera, warehouse, customs, pharmacy stations."""
from __future__ import annotations

from django.utils import timezone

from apps.mobile.models import DeviceRegistration, OfflineScanQueue
from apps.serialization.operations import record_serial_scan
from apps.verification.services import sovereign_verify


SCANNER_TYPES = ("mobile_camera", "warehouse_scanner", "customs_scanner", "pharmacy_station", "regulator_tablet")


def ingest_scan(
    *,
    request,
    raw_scan: str,
    scan_source: str,
    scanner_type: str = "mobile_camera",
    device_id: str | None = None,
    latitude=None,
    longitude=None,
    replay_nonce: str = "",
    offline: bool = False,
) -> dict:
    if offline and device_id:
        device = DeviceRegistration.objects.filter(device_id=device_id).first()
        if device:
            OfflineScanQueue.objects.create(
                device=device,
                raw_scan=raw_scan,
                scan_source=scan_source,
                scanner_type=scanner_type,
                latitude=latitude,
                longitude=longitude,
                replay_nonce=replay_nonce,
            )
            return {"queued": True, "sync_status": "pending"}

    record_serial_scan(
        raw_scan=raw_scan,
        scan_source=scan_source,
        scanner_type=scanner_type,
        device_fingerprint=device_id or "",
        replay_nonce=replay_nonce,
        latitude=latitude,
        longitude=longitude,
    )
    return sovereign_verify(
        request=request,
        serial_number=raw_scan,
        latitude=latitude,
        longitude=longitude,
        device_id=device_id,
    )


def sync_offline_queue(*, device: DeviceRegistration, request) -> dict:
    pending = OfflineScanQueue.objects.filter(device=device, sync_status="pending")[:50]
    synced = 0
    failed = 0
    for row in pending:
        try:
            ingest_scan(
                request=request,
                raw_scan=row.raw_scan,
                scan_source=row.scan_source,
                scanner_type=row.scanner_type,
                device_id=device.device_id,
                latitude=row.latitude,
                longitude=row.longitude,
                replay_nonce=row.replay_nonce,
                offline=False,
            )
            row.sync_status = "synced"
            row.synced_at = timezone.now()
            row.save(update_fields=["sync_status", "synced_at", "updated_at"])
            synced += 1
        except Exception as exc:
            row.sync_attempts += 1
            row.last_error = str(exc)[:500]
            row.save(update_fields=["sync_attempts", "last_error", "updated_at"])
            failed += 1
    device.last_sync_at = timezone.now()
    device.save(update_fields=["last_sync_at", "updated_at"])
    return {"synced": synced, "failed": failed}
