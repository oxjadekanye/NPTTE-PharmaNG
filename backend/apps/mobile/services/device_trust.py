"""Phase 22 — mobile device trust scoring and registration."""
from __future__ import annotations

import hashlib
from decimal import Decimal

from django.utils import timezone

from apps.mobile.models import DeviceRegistration
from apps.mobile.services.mobile_audit import record_mobile_audit


def _risk_from_flags(*, is_emulator: bool, is_rooted: bool, suspicious: bool) -> str:
    if suspicious or is_rooted:
        return "high"
    if is_emulator:
        return "medium"
    return "low"


def register_device_trust(
    *,
    request,
    device_id: str,
    fingerprint: str,
    platform: str,
    app_version: str,
    os_version: str = "",
    is_emulator: bool = False,
    is_rooted: bool = False,
    suspicious: bool = False,
    biometric_capable: bool = False,
) -> DeviceRegistration:
    fp_hash = hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:64]
    risk = _risk_from_flags(is_emulator=is_emulator, is_rooted=is_rooted, suspicious=suspicious)
    trusted = "trusted" if risk == "low" and not suspicious else "pending"
    if risk == "high":
        trusted = "suspended"

    device, _created = DeviceRegistration.objects.update_or_create(
        device_id=device_id,
        defaults={
            "device_type": platform or "unknown",
            "platform": platform,
            "organisation_id": request.user.organisation_id,
            "app_version": app_version,
            "os_version": os_version,
            "fingerprint_hash": fp_hash,
            "assigned_role_code": getattr(request.user.role, "code", "") if request.user.role_id else "",
            "trusted_status": trusted,
            "device_risk_level": risk,
            "is_emulator": is_emulator,
            "is_rooted_flag": is_rooted,
            "suspicious_device": suspicious,
            "biometric_capable": biometric_capable,
            "last_sync_at": timezone.now(),
            "last_heartbeat_at": timezone.now(),
            "trust_score": Decimal("85" if trusted == "trusted" else "45"),
            "created_by": request.user,
        },
    )
    record_mobile_audit(
        request=request,
        device=device,
        action_type="device.trust.register",
        payload={"trusted_status": trusted, "device_risk_level": risk},
    )
    return device


def device_heartbeat(
    *,
    request,
    device_id: str,
    app_version: str = "",
    rotate_session: bool = False,
) -> dict:
    import uuid

    device = DeviceRegistration.objects.filter(device_id=device_id).first()
    if not device:
        return {"ok": False, "reason": "device_not_found"}

    device.last_heartbeat_at = timezone.now()
    device.last_sync_at = timezone.now()
    if app_version:
        device.app_version = app_version
    new_token = None
    if rotate_session or device.device_risk_level == "high":
        new_token = uuid.uuid4().hex[:32]
        device.offline_sync_token = new_token
    device.save(
        update_fields=[
            "last_heartbeat_at",
            "last_sync_at",
            "app_version",
            "offline_sync_token",
            "updated_at",
        ]
    )
    record_mobile_audit(
        request=request,
        device=device,
        action_type="device.heartbeat",
        payload={"rotate_session": rotate_session},
    )
    return {
        "ok": True,
        "trusted_status": device.trusted_status,
        "device_risk_level": device.device_risk_level,
        "last_seen": device.last_heartbeat_at.isoformat() if device.last_heartbeat_at else None,
        "offline_sync_token": new_token or device.offline_sync_token,
    }
