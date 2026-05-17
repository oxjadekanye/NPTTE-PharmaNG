"""Enterprise security utilities — HMAC tokens and request fingerprinting."""
from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any

from django.conf import settings


def get_verification_secret() -> bytes:
    key = getattr(settings, "NPTTE_VERIFICATION_HMAC_SECRET", None) or settings.SECRET_KEY
    return key.encode("utf-8")


def sign_verification_token(payload: dict[str, Any]) -> str:
    """Create HMAC signature for QR verification tokens."""
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hmac.new(get_verification_secret(), body.encode(), hashlib.sha256).hexdigest()


def verify_signed_token(payload: dict[str, Any], signature: str) -> bool:
    expected = sign_verification_token(payload)
    return hmac.compare_digest(expected, signature)


def request_fingerprint(request) -> str:
    """Stable fingerprint for suspicious activity monitoring."""
    parts = [
        request.META.get("REMOTE_ADDR", ""),
        request.META.get("HTTP_USER_AGENT", ""),
        request.META.get("HTTP_ACCEPT_LANGUAGE", ""),
    ]
    raw = "|".join(parts)
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def verify_api_signature(payload: str, signature: str, timestamp: str, max_age_seconds: int = 300) -> bool:
    """HMAC API signature with replay window (timestamp in epoch seconds)."""
    import time

    try:
        ts = int(timestamp)
    except (TypeError, ValueError):
        return False
    if abs(time.time() - ts) > max_age_seconds:
        return False
    body = f"{timestamp}.{payload}"
    expected = hmac.new(get_verification_secret(), body.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def log_security_threat(request, threat_type: str, severity: str = "medium", **details):
    """Record suspicious activity for regulator review."""
    from apps.core.security_models import SecurityThreatLog

    SecurityThreatLog.objects.create(
        threat_type=threat_type,
        severity=severity,
        request_fingerprint=request_fingerprint(request),
        client_ip=request.META.get("REMOTE_ADDR"),
        endpoint=request.path[:255],
        user_agent=(request.META.get("HTTP_USER_AGENT") or "")[:512],
        details=details,
    )
