"""Citizen verification and trust scoring."""
from __future__ import annotations

import uuid
from decimal import Decimal

from django.utils import timezone

from apps.citizen.models import CitizenVerificationSession, VerificationHistory
from apps.pharmacies.models import PharmacyProfile


def get_or_create_session(*, request) -> CitizenVerificationSession:
    from apps.core.security import request_fingerprint

    fp = request_fingerprint(request)
    session, _ = CitizenVerificationSession.objects.get_or_create(
        device_fingerprint=fp,
        defaults={
            "session_token": uuid.uuid4().hex,
            "client_ip": request.META.get("REMOTE_ADDR"),
        },
    )
    return session


def record_citizen_verification(*, session: CitizenVerificationSession, serial_number: str, outcome: str):
    VerificationHistory.objects.create(
        session=session,
        serial_number=serial_number,
        outcome=outcome,
        verified_at=timezone.now(),
    )
    session.verification_count += 1
    session.last_verified_at = timezone.now()
    session.save(update_fields=["verification_count", "last_verified_at", "updated_at"])


def pharmacy_trust_score(pharmacy: PharmacyProfile) -> Decimal:
    """Heuristic public trust score for citizen-facing pharmacy discovery."""
    score = Decimal("70")
    if pharmacy.is_national_registry_verified:
        score += Decimal("20")
    if pharmacy.pharmacy_license_number:
        score += Decimal("10")
    return min(score, Decimal("100"))
