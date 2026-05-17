"""Sovereign national medicine verification engine."""
from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from apps.alerts.services import create_national_alert
from apps.core.constants import AlertCategory, AlertSeverity, VerificationOutcome, VerificationStatus
from apps.core.security import request_fingerprint, verify_signed_token
from apps.fraud_detection.services import create_fraud_flag
from apps.serialization.models import ProductSerial
from apps.serialization.services import ensure_qr_payload
from apps.traceability.services import check_batch_recall
from apps.verification.models import VerificationEvent, VerificationScanLog


def detect_counterfeit_cluster(*, serial_number: str, latitude=None, longitude=None) -> bool:
    """
    Detect if same serial scanned across distant regions within short window.

    Returns True if cluster anomaly detected.
    """
    since = timezone.now() - timedelta(hours=24)
    recent = VerificationScanLog.objects.filter(
        serial_number=serial_number,
        created_at__gte=since,
        latitude__isnull=False,
        longitude__isnull=False,
    ).exclude(latitude=latitude, longitude=longitude)

    if recent.count() < 2:
        return False

    if latitude is None or longitude is None:
        return recent.count() >= 3

    from apps.geolocation.services import haversine_km

    for scan in recent[:10]:
        if scan.latitude and scan.longitude:
            dist = haversine_km(latitude, longitude, scan.latitude, scan.longitude)
            if dist > 100:
                create_national_alert(
                    alert_type=AlertCategory.COUNTERFEIT,
                    title=f"Counterfeit cluster: {serial_number}",
                    description="Serial verified in distant regions within 24 hours.",
                    severity=AlertSeverity.CRITICAL,
                    risk_score=Decimal("90"),
                    evidence_payload={
                        "serial_number": serial_number,
                        "scan_count": recent.count() + 1,
                    },
                )
                create_fraud_flag(
                    flag_type="counterfeit_cluster",
                    risk_score=Decimal("90"),
                    description=f"Distant region scans for {serial_number}",
                )
                return True
    return False


def sovereign_verify(
    *,
    request,
    serial_number: str = "",
    qr_token: str = "",
    latitude=None,
    longitude=None,
) -> dict:
    """
    Execute sovereign verification and return national response payload.

    Maintains backward-compatible fields for Phase 3 clients.
    """
    serial_number = (serial_number or "").strip()
    fingerprint = request_fingerprint(request)
    ip = request.META.get("REMOTE_ADDR")
    ua = (request.META.get("HTTP_USER_AGENT") or "")[:512]

    if not serial_number and qr_token:
        serial_number = qr_token.split("/")[-1].strip()

    if not serial_number:
        VerificationScanLog.objects.create(
            serial_number="",
            outcome=VerificationOutcome.INVALID_SERIAL,
            device_fingerprint=fingerprint,
            client_ip=ip,
            user_agent=ua,
            latitude=latitude,
            longitude=longitude,
        )
        return _response(
            outcome=VerificationOutcome.INVALID_SERIAL,
            is_authentic=False,
            message="Serial number required.",
            status_code=400,
        )

    try:
        product_serial = ProductSerial.objects.select_related(
            "batch", "batch__product", "batch__manufacturing_site"
        ).get(serial_number=serial_number)
    except ProductSerial.DoesNotExist:
        VerificationScanLog.objects.create(
            serial_number=serial_number,
            outcome=VerificationOutcome.INVALID_SERIAL,
            device_fingerprint=fingerprint,
            client_ip=ip,
            user_agent=ua,
            latitude=latitude,
            longitude=longitude,
        )
        return _response(
            outcome=VerificationOutcome.INVALID_SERIAL,
            is_authentic=False,
            message="Serial not found in national registry.",
            status_code=404,
        )

    if qr_token and product_serial.qr_token_signature:
        if qr_token != product_serial.qr_token_signature and not verify_signed_token(
            {"serial": serial_number, "batch_id": str(product_serial.batch_id)}, qr_token
        ):
            outcome = VerificationOutcome.COUNTERFEIT_SUSPECTED
            _log_scan(product_serial, serial_number, outcome, fingerprint, ip, ua, latitude, longitude, qr_token)
            return _response(
                outcome=outcome,
                is_authentic=False,
                message="QR token verification failed.",
                product_serial=product_serial,
                status_code=403,
            )

  # Duplicate rapid scan detection
    recent_same = VerificationScanLog.objects.filter(
        serial_number=serial_number,
        device_fingerprint=fingerprint,
        created_at__gte=timezone.now() - timedelta(minutes=5),
    ).count()
    if recent_same >= 3:
        outcome = VerificationOutcome.DUPLICATE_SCAN_DETECTED
        _log_scan(product_serial, serial_number, outcome, fingerprint, ip, ua, latitude, longitude, qr_token)
        detect_counterfeit_cluster(serial_number=serial_number, latitude=latitude, longitude=longitude)
        return _response(
            outcome=outcome,
            is_authentic=False,
            message="Repeated verification scans detected.",
            product_serial=product_serial,
        )

    recall = check_batch_recall(product_serial.batch)
    batch = product_serial.batch
    if batch.expiry_date and batch.expiry_date < timezone.now().date():
        outcome = VerificationOutcome.EXPIRED
        _log_scan(product_serial, serial_number, outcome, fingerprint, ip, ua, latitude, longitude, qr_token)
        return _response(outcome=outcome, is_authentic=False, message="Medication batch expired.", product_serial=product_serial)

    if recall:
        outcome = VerificationOutcome.RECALLED
        _log_scan(product_serial, serial_number, outcome, fingerprint, ip, ua, latitude, longitude, qr_token)
        return _response(outcome=outcome, is_authentic=False, message="Batch under national recall.", product_serial=product_serial)

    if product_serial.is_dispensed:
        outcome = VerificationOutcome.COUNTERFEIT_SUSPECTED
        msg = "Serial already dispensed — verify point of sale."
        _log_scan(product_serial, serial_number, outcome, fingerprint, ip, ua, latitude, longitude, qr_token)
        return _response(outcome=outcome, is_authentic=False, message=msg, product_serial=product_serial)

    from apps.core.constants import RegulatorBatchStatus

    if batch.regulator_status != RegulatorBatchStatus.APPROVED:
        outcome = VerificationOutcome.UNREGISTERED_PRODUCT
        _log_scan(product_serial, serial_number, outcome, fingerprint, ip, ua, latitude, longitude, qr_token)
        return _response(outcome=outcome, is_authentic=False, message="Batch pending regulator approval.", product_serial=product_serial)

    ensure_qr_payload(product_serial)
    product_serial.scan_count += 1
    product_serial.save(update_fields=["scan_count", "updated_at"])

    outcome = VerificationOutcome.AUTHENTIC
    _log_scan(product_serial, serial_number, outcome, fingerprint, ip, ua, latitude, longitude, qr_token)
    detect_counterfeit_cluster(serial_number=serial_number, latitude=latitude, longitude=longitude)

    VerificationEvent.objects.create(
        product_serial=product_serial,
        channel="qr",
        is_authentic=True,
        verification_message="Authentic NPTTE registered medicine.",
        client_ip=ip,
        user_agent=ua,
    )

    return _response(
        outcome=outcome,
        is_authentic=True,
        message="Authentic medicine pack registered with NPTTE.",
        product_serial=product_serial,
    )


def _log_scan(serial, serial_number, outcome, fingerprint, ip, ua, lat, lon, qr_token):
    VerificationScanLog.objects.create(
        product_serial=serial,
        serial_number=serial_number,
        outcome=outcome,
        qr_token=qr_token or "",
        device_fingerprint=fingerprint,
        client_ip=ip,
        user_agent=ua,
        latitude=lat,
        longitude=lon,
    )


def _response(*, outcome, is_authentic, message, product_serial=None, status_code=200):
    legacy_status = VerificationStatus.VERIFIED if is_authentic else VerificationStatus.FAILED
    if outcome == VerificationOutcome.RECALLED:
        legacy_status = VerificationStatus.RECALLED
    elif outcome in (VerificationOutcome.COUNTERFEIT_SUSPECTED, VerificationOutcome.DUPLICATE_SCAN_DETECTED):
        legacy_status = VerificationStatus.SUSPICIOUS

    data = {
        "outcome": outcome,
        "is_authentic": is_authentic,
        "verification_status": legacy_status,
        "serial_number": product_serial.serial_number if product_serial else "",
    }
    if product_serial:
        data.update(
            {
                "serial_number": product_serial.serial_number,
                "qr_payload": product_serial.qr_payload,
                "barcode_payload": product_serial.barcode_payload,
                "scan_count": product_serial.scan_count,
                "product": {
                    "name": product_serial.batch.product.name,
                    "brand_name": product_serial.batch.product.brand_name,
                    "strength": product_serial.batch.product.strength,
                    "dosage_form": product_serial.batch.product.dosage_form,
                    "dosage_guidance": product_serial.batch.product.dosage_guidance,
                },
                "batch_number": product_serial.batch.batch_number,
                "expiry_date": product_serial.batch.expiry_date,
                "regulator_status": product_serial.batch.regulator_status,
                "verified_at": timezone.now().isoformat(),
            }
        )
    return {"data": data, "message": message, "status_code": status_code}
