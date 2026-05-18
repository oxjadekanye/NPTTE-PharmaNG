"""Sovereign national medicine verification engine (Phase 8 enhanced)."""
from __future__ import annotations

import hashlib
from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from apps.alerts.services import create_national_alert
from apps.core.constants import (
    AlertCategory,
    AlertSeverity,
    BatchLifecycleStatus,
    RegulatorBatchStatus,
    VerificationOutcome,
    VerificationStatus,
)
from apps.core.security import request_fingerprint, verify_signed_token
from apps.fraud_detection.services import create_fraud_flag
from apps.products.models import ProductBatch
from apps.serialization.gs1 import decode_gs1_scan, resolve_serial_from_scan
from apps.serialization.models import ProductSerial
from apps.serialization.operations import record_serial_scan
from apps.serialization.services import ensure_qr_payload
from apps.traceability.services import check_batch_recall
from apps.verification.models import VerificationEvent, VerificationScanLog

EXCESSIVE_PUBLIC_SCANS = 75


def _device_fingerprint(request, device_id: str | None) -> str:
    base = request_fingerprint(request)
    if device_id:
        return hashlib.sha256(f"{base}:{device_id}".encode()).hexdigest()[:32]
    return base


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


def _manufacturer_label(product) -> str:
    m = getattr(product, "manufacturer", None)
    if m is None:
        return ""
    return getattr(m, "legal_name", None) or getattr(m, "trading_name", None) or str(m)


def _result_and_flags(*, outcome: str, is_authentic: bool, duplicate_soft: bool = False) -> dict:
    duplicate_scan_warning = duplicate_soft or outcome == VerificationOutcome.DUPLICATE_SCAN_DETECTED
    if outcome == VerificationOutcome.AUTHENTIC:
        bucket = "authentic"
    elif outcome == VerificationOutcome.INVALID_SERIAL:
        bucket = "invalid"
    elif outcome == VerificationOutcome.EXPIRED:
        bucket = "expired"
    elif outcome == VerificationOutcome.RECALLED:
        bucket = "recalled"
    elif outcome == VerificationOutcome.DUPLICATE_SCAN_DETECTED:
        bucket = "duplicate_scan_warning"
    else:
        bucket = "suspicious"
    safety = {
        VerificationOutcome.AUTHENTIC: "This pack matches the national NPTTE registry. Follow dosage on the label or as directed by your pharmacist.",
        VerificationOutcome.INVALID_SERIAL: "Do not use this medicine. Report the outlet to NAFDAC via the NPTTE citizen channel.",
        VerificationOutcome.EXPIRED: "Do not use expired medicines. Dispose safely at an authorised collection point.",
        VerificationOutcome.RECALLED: "National recall: do not use. Return to pharmacy or contact NAFDAC.",
        VerificationOutcome.COUNTERFEIT_SUSPECTED: "Elevated risk signal — do not use until verified by a licensed pharmacist.",
        VerificationOutcome.DUPLICATE_SCAN_DETECTED: "Unusual scan pattern — verify packaging and purchase source.",
        VerificationOutcome.UNREGISTERED_PRODUCT: "Batch not cleared for circulation — do not use.",
    }.get(outcome, "If in doubt, consult a pharmacist before use.")
    next_action = {
        VerificationOutcome.AUTHENTIC: "Retain packaging for your records.",
        VerificationOutcome.INVALID_SERIAL: "Submit a counterfeit report via NPTTE Citizen.",
        VerificationOutcome.EXPIRED: "Check alternative batches with your pharmacy.",
        VerificationOutcome.RECALLED: "Follow national recall instructions on NAFDAC channels.",
        VerificationOutcome.COUNTERFEIT_SUSPECTED: "Request pharmacy verification and supply-chain receipt.",
        VerificationOutcome.DUPLICATE_SCAN_DETECTED: "Compare serial with packaging; contact regulator if mismatch.",
        VerificationOutcome.UNREGISTERED_PRODUCT: "Await manufacturer regulatory clearance.",
    }.get(outcome, "Contact NPTTE support if you need assistance.")
    return {
        "result": bucket,
        "duplicate_scan_warning": duplicate_scan_warning,
        "safety_message": safety,
        "next_action": next_action,
    }


def sovereign_verify(
    *,
    request,
    serial_number: str = "",
    qr_token: str = "",
    latitude=None,
    longitude=None,
    device_id: str | None = None,
    pharmacy_organisation_id=None,
) -> dict:
    """
    Execute sovereign verification and return national response payload.

    Phase 8: optional device_id for scan analytics; pharmacy_organisation_id enforces custody on dispense checks.
    """
    raw_scan = (serial_number or qr_token or "").strip()
    serial_number = resolve_serial_from_scan(raw_scan) if raw_scan else ""
    gs1_decoded = decode_gs1_scan(raw_scan) if raw_scan else None
    fingerprint = _device_fingerprint(request, device_id)
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
            "batch", "batch__product", "batch__product__manufacturer", "batch__manufacturing_site"
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

    batch = product_serial.batch
    batch.refresh_from_db()

    if batch.lifecycle_status in (BatchLifecycleStatus.SUSPENDED, BatchLifecycleStatus.DESTROYED):
        outcome = VerificationOutcome.COUNTERFEIT_SUSPECTED
        _log_scan(product_serial, serial_number, outcome, fingerprint, ip, ua, latitude, longitude, qr_token)
        return _response(
            outcome=outcome,
            is_authentic=False,
            message="Batch is suspended or destroyed in the national registry.",
            product_serial=product_serial,
            status_code=403,
        )

    if pharmacy_organisation_id and product_serial.custody_organisation_id:
        if str(product_serial.custody_organisation_id) != str(pharmacy_organisation_id):
            outcome = VerificationOutcome.COUNTERFEIT_SUSPECTED
            _log_scan(product_serial, serial_number, outcome, fingerprint, ip, ua, latitude, longitude, qr_token)
            return _response(
                outcome=outcome,
                is_authentic=False,
                message="Serial custody does not match this pharmacy.",
                product_serial=product_serial,
                status_code=403,
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

    if batch.expiry_date and batch.expiry_date < timezone.now().date():
        outcome = VerificationOutcome.EXPIRED
        ProductBatch.objects.filter(pk=batch.pk).update(
            lifecycle_status=BatchLifecycleStatus.EXPIRED, updated_at=timezone.now()
        )
        _log_scan(product_serial, serial_number, outcome, fingerprint, ip, ua, latitude, longitude, qr_token)
        return _response(outcome=outcome, is_authentic=False, message="Medication batch expired.", product_serial=product_serial)

    recall = check_batch_recall(batch)
    if recall or batch.lifecycle_status == BatchLifecycleStatus.RECALLED:
        outcome = VerificationOutcome.RECALLED
        _log_scan(product_serial, serial_number, outcome, fingerprint, ip, ua, latitude, longitude, qr_token)
        return _response(outcome=outcome, is_authentic=False, message="Batch under national recall.", product_serial=product_serial)

    if product_serial.is_dispensed:
        outcome = VerificationOutcome.COUNTERFEIT_SUSPECTED
        msg = "Serial already dispensed — verify point of sale."
        _log_scan(product_serial, serial_number, outcome, fingerprint, ip, ua, latitude, longitude, qr_token)
        return _response(outcome=outcome, is_authentic=False, message=msg, product_serial=product_serial)

    if batch.regulator_status != RegulatorBatchStatus.APPROVED:
        outcome = VerificationOutcome.UNREGISTERED_PRODUCT
        _log_scan(product_serial, serial_number, outcome, fingerprint, ip, ua, latitude, longitude, qr_token)
        return _response(outcome=outcome, is_authentic=False, message="Batch pending regulator approval.", product_serial=product_serial)

    if batch.lifecycle_status not in (BatchLifecycleStatus.APPROVED, BatchLifecycleStatus.ACTIVE):
        outcome = VerificationOutcome.UNREGISTERED_PRODUCT
        _log_scan(product_serial, serial_number, outcome, fingerprint, ip, ua, latitude, longitude, qr_token)
        return _response(
            outcome=outcome,
            is_authentic=False,
            message="Batch lifecycle does not permit public verification.",
            product_serial=product_serial,
        )

    if product_serial.scan_count >= EXCESSIVE_PUBLIC_SCANS:
        outcome = VerificationOutcome.COUNTERFEIT_SUSPECTED
        _log_scan(product_serial, serial_number, outcome, fingerprint, ip, ua, latitude, longitude, qr_token)
        return _response(
            outcome=outcome,
            is_authentic=False,
            message="Excessive verification attempts for this serial — possible diversion.",
            product_serial=product_serial,
        )

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

    duplicate_soft = product_serial.scan_count > 1
    from apps.ai_engine.services import calculate_counterfeit_probability

    counterfeit_probability = float(calculate_counterfeit_probability(serial_number=serial_number))
    product_serial.counterfeit_probability = counterfeit_probability
    product_serial.save(update_fields=["counterfeit_probability", "updated_at"])
    record_serial_scan(
        raw_scan=raw_scan or serial_number,
        scan_source="citizen",
        scanner_type="public_verify",
        outcome=outcome,
        latitude=latitude,
        longitude=longitude,
        device_fingerprint=fingerprint,
    )
    resp = _response(
        outcome=outcome,
        is_authentic=True,
        message="Authentic medicine pack registered with NPTTE.",
        product_serial=product_serial,
        duplicate_soft=duplicate_soft,
    )
    resp["data"]["counterfeit_probability"] = counterfeit_probability
    if gs1_decoded:
        resp["data"]["scan_metadata"] = {
            "format_hint": gs1_decoded.format_hint,
            "gtin": gs1_decoded.gtin,
        }
    return resp


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


def _response(
    *,
    outcome,
    is_authentic,
    message,
    product_serial=None,
    status_code=200,
    duplicate_soft: bool = False,
):
    legacy_status = VerificationStatus.VERIFIED if is_authentic else VerificationStatus.FAILED
    if outcome == VerificationOutcome.RECALLED:
        legacy_status = VerificationStatus.RECALLED
    elif outcome in (VerificationOutcome.COUNTERFEIT_SUSPECTED, VerificationOutcome.DUPLICATE_SCAN_DETECTED):
        legacy_status = VerificationStatus.SUSPICIOUS

    flags = _result_and_flags(outcome=outcome, is_authentic=is_authentic, duplicate_soft=duplicate_soft)
    data = {
        "outcome": outcome,
        "is_authentic": is_authentic,
        "verification_status": legacy_status,
        "serial_number": product_serial.serial_number if product_serial else "",
        **flags,
    }
    if product_serial:
        batch = product_serial.batch
        cp = float(product_serial.counterfeit_probability or 0)
        data.update(
            {
                "serial_number": product_serial.serial_number,
                "qr_payload": product_serial.qr_payload,
                "barcode_payload": product_serial.barcode_payload,
                "scan_count": product_serial.scan_count,
                "counterfeit_probability": cp,
                "product": {
                    "name": batch.product.name,
                    "brand_name": batch.product.brand_name,
                    "strength": batch.product.strength,
                    "dosage_form": batch.product.dosage_form,
                    "dosage_guidance": batch.product.dosage_guidance,
                },
                "manufacturer": _manufacturer_label(batch.product),
                "batch_number": batch.batch_number,
                "expiry_date": batch.expiry_date.isoformat() if batch.expiry_date else None,
                "regulator_status": batch.regulator_status,
                "lifecycle_status": batch.lifecycle_status,
                "verified_at": timezone.now().isoformat(),
            }
        )
    return {"data": data, "message": message, "status_code": status_code}
