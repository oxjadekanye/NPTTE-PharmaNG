"""Phase 22 — field evidence capture."""
from __future__ import annotations

from apps.mobile.models import DeviceRegistration, MobileFieldEvidence
from apps.mobile.services.mobile_audit import record_mobile_audit
from apps.streambus.services.bus import publish_operational_event


def create_field_evidence(
    *,
    request,
    device_id: str,
    evidence_type: str,
    notes: str = "",
    serial_number: str = "",
    case_id=None,
    latitude=None,
    longitude=None,
    photos: list | None = None,
) -> MobileFieldEvidence:
    device = DeviceRegistration.objects.filter(device_id=device_id).first()
    # Cap photo payload size for DB safety
    safe_photos = []
    for p in (photos or [])[:6]:
        if isinstance(p, dict):
            b64 = str(p.get("base64", ""))[:120000]
            safe_photos.append(
                {
                    "id": p.get("id"),
                    "mime": p.get("mime", "image/jpeg"),
                    "base64": b64,
                    "upload_status": p.get("upload_status", "pending"),
                }
            )

    ev = MobileFieldEvidence.objects.create(
        device=device,
        actor=request.user,
        evidence_type=evidence_type,
        notes=notes,
        serial_number=serial_number,
        case_id=case_id,
        latitude=latitude,
        longitude=longitude,
        photos=safe_photos,
        sync_status=MobileFieldEvidence.SYNC_SYNCED,
        created_by=request.user,
    )
    record_mobile_audit(
        request=request,
        device=device,
        action_type="evidence.capture",
        payload={"evidence_type": evidence_type, "serial_number": serial_number},
        evidence=ev,
        latitude=latitude,
        longitude=longitude,
    )
    publish_operational_event(
        event_type="mobile.evidence.captured",
        payload={
            "evidence_id": str(ev.id),
            "evidence_type": evidence_type,
            "device_id": device_id,
            "stream_channel": "investigation",
        },
        severity="INFO",
    )
    return ev


def sync_pending_evidence(*, request, device_id: str) -> dict:
    device = DeviceRegistration.objects.filter(device_id=device_id).first()
    if not device:
        return {"synced": 0}
    pending = MobileFieldEvidence.objects.filter(
        device=device, sync_status=MobileFieldEvidence.SYNC_PENDING
    )[:20]
    count = 0
    for ev in pending:
        ev.sync_status = MobileFieldEvidence.SYNC_SYNCED
        ev.save(update_fields=["sync_status", "updated_at"])
        count += 1
    return {"synced": count}
