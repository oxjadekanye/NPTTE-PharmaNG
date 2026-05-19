"""Phase 22 — mobile operational audit trail."""
from __future__ import annotations

from apps.mobile.models import DeviceRegistration, MobileFieldEvidence, MobileOperationalAudit


def record_mobile_audit(
    *,
    request,
    action_type: str,
    payload: dict | None = None,
    device: DeviceRegistration | None = None,
    evidence: MobileFieldEvidence | None = None,
    sync_status: str = "synced",
    latitude=None,
    longitude=None,
) -> MobileOperationalAudit:
    device_id = (payload or {}).get("device_id") if payload else None
    if not device and device_id:
        device = DeviceRegistration.objects.filter(device_id=device_id).first()

    return MobileOperationalAudit.objects.create(
        device=device,
        actor=request.user if request.user.is_authenticated else None,
        action_type=action_type,
        payload=payload or {},
        latitude=latitude,
        longitude=longitude,
        sync_status=sync_status,
        evidence=evidence,
        created_by=request.user if request.user.is_authenticated else None,
    )
