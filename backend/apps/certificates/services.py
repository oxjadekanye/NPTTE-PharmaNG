"""Certificate issuance and verification."""
from __future__ import annotations

import hashlib
import uuid
from datetime import timedelta

from django.utils import timezone

from apps.certificates.models import DigitalRegulatoryCertificate
from apps.core.security import sign_verification_token


def issue_certificate(
    *,
    certificate_type: str,
    subject_label: str,
    batch=None,
    payload: dict | None = None,
    actor=None,
    ttl_days: int = 365,
) -> DigitalRegulatoryCertificate:
    cert_no = f"NPTTE-CERT-{uuid.uuid4().hex[:12].upper()}"
    qr_code = f"NPTTE-QR-CERT-{uuid.uuid4().hex[:16]}"
    body = payload or {}
    tamper = hashlib.sha256(f"{cert_no}:{subject_label}:{body}".encode()).hexdigest()
    signature = sign_verification_token({"cert": cert_no, "tamper": tamper})
    now = timezone.now()
    return DigitalRegulatoryCertificate.objects.create(
        certificate_number=cert_no,
        certificate_type=certificate_type,
        batch=batch,
        subject_label=subject_label,
        issued_at=now,
        expires_at=now + timedelta(days=ttl_days),
        qr_verification_code=qr_code,
        digital_signature=signature,
        tamper_hash=tamper,
        payload=body,
        issued_by=actor,
        created_by=actor,
    )


def verify_certificate(*, qr_verification_code: str) -> dict:
    cert = DigitalRegulatoryCertificate.objects.filter(qr_verification_code=qr_verification_code).first()
    if not cert:
        return {"valid": False, "message": "Certificate not found"}
    expected = hashlib.sha256(f"{cert.certificate_number}:{cert.subject_label}:{cert.payload}".encode()).hexdigest()
    tampered = expected != cert.tamper_hash
    expired = cert.expires_at and cert.expires_at < timezone.now()
    return {
        "valid": not tampered and not expired,
        "tampered": tampered,
        "expired": bool(expired),
        "certificate_number": cert.certificate_number,
        "certificate_type": cert.certificate_type,
        "subject_label": cert.subject_label,
        "issued_at": cert.issued_at.isoformat(),
    }
