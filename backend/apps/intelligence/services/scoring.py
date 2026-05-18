"""Deterministic national risk scoring (rules-based, no ML)."""
from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from django.db.models import Count
from django.utils import timezone

from apps.organisations.models import Organisation
from apps.products.models import Product, ProductBatch
from apps.scanning.models import ScanEvent
from apps.traceability.models import BatchRecall, PharmacyRecallAcknowledgement, RecallExecutionCampaign


def _status_from_score(score: float) -> str:
    if score >= 85:
        return "critical"
    if score >= 65:
        return "red"
    if score >= 40:
        return "amber"
    return "green"


def _result(*, score: float, confidence: float, reasons: list, actions: list) -> dict:
    return {
        "score": round(min(100, max(0, score)), 1),
        "status": _status_from_score(score),
        "confidence": round(min(100, max(0, confidence)), 1),
        "reasons": reasons,
        "recommended_actions": actions,
    }


def calculate_national_risk() -> dict:
    since = timezone.now() - timedelta(hours=24)
    suspicious = ScanEvent.objects.filter(created_at__gte=since).filter(
        outcome_label__icontains="suspicious"
    ).count()
    invalid = ScanEvent.objects.filter(created_at__gte=since).filter(
        outcome_label__icontains="invalid"
    ).count()
    recalls = BatchRecall.objects.filter(effective_at__gte=since).count()
    score = min(100, suspicious * 4 + invalid * 3 + recalls * 8 + 15)
    return _result(
        score=score,
        confidence=72,
        reasons=[
            f"{suspicious} suspicious scans (24h)",
            f"{invalid} invalid serial scans (24h)",
            f"{recalls} active recall events",
        ],
        actions=["Review national threat dashboard", "Run correlation engine"],
    )


def calculate_organisation_risk(*, organisation: Organisation) -> dict:
    since = timezone.now() - timedelta(days=7)
    scans = ScanEvent.objects.filter(organisation=organisation, created_at__gte=since)
    suspicious = scans.filter(outcome_label__icontains="suspicious").count()
    duplicate = scans.filter(outcome_label__icontains="duplicate").count()
    delayed_ack = 0
    campaigns = RecallExecutionCampaign.objects.filter(created_at__gte=since)
    for c in campaigns:
        if c.pharmacies_targeted > c.pharmacies_acknowledged:
            if not PharmacyRecallAcknowledgement.objects.filter(
                campaign=c, pharmacy_organisation=organisation, acknowledged_at__isnull=False
            ).exists():
                delayed_ack += 1
    score = min(100, suspicious * 12 + duplicate * 8 + delayed_ack * 15)
    return _result(
        score=score,
        confidence=68,
        reasons=[
            f"{suspicious} suspicious scans (7d)",
            f"{duplicate} duplicate scans",
            f"{delayed_ack} delayed recall acknowledgements",
        ],
        actions=["Schedule compliance review", "Verify custody chain"],
    )


def calculate_product_risk(*, product: Product) -> dict:
    since = timezone.now() - timedelta(days=14)
    serials = ScanEvent.objects.filter(created_at__gte=since).filter(
        serial_number__icontains=product.name[:10] if product.name else ""
    )
    suspicious = serials.filter(outcome_label__icontains="suspicious").count()
    recalled = product.batches.filter(recalls__isnull=False).exists()
    expired_batches = product.batches.filter(expiry_date__lt=timezone.now().date()).count()
    score = min(100, suspicious * 10 + (25 if recalled else 0) + expired_batches * 5)
    counterfeit_prob = min(100, suspicious * 15 + (30 if recalled else 0))
    result = _result(
        score=score,
        confidence=65,
        reasons=[
            f"{suspicious} suspicious scans linked to product",
            "Batch under recall" if recalled else "No active recall",
            f"{expired_batches} expired batches",
        ],
        actions=["Inspect distribution channels", "Escalate recall if needed"],
    )
    result["counterfeit_probability"] = counterfeit_prob
    return result


def calculate_regional_risk(*, region_state: str) -> dict:
    since = timezone.now() - timedelta(days=7)
    scans = ScanEvent.objects.filter(created_at__gte=since, organisation__state__iexact=region_state)
    total = scans.count()
    suspicious = scans.filter(outcome_label__icontains="suspicious").count()
    density = total
    rate = (suspicious * 100 / total) if total else 0
    score = min(100, density // 5 + rate * 0.8)
    result = _result(
        score=score,
        confidence=60 if total > 5 else 40,
        reasons=[f"{total} scans in {region_state}", f"{suspicious} suspicious ({rate:.0f}%)"],
        actions=["Regional inspection sweep", "Monitor pharmacy clusters"],
    )
    result["scan_density"] = density
    return result


def calculate_counterfeit_probability(*, serial_number: str) -> dict:
    try:
        from apps.ai_engine.services import calculate_counterfeit_probability as ai_prob

        prob = float(ai_prob(serial_number=serial_number))
    except Exception:
        scans = ScanEvent.objects.filter(serial_number=serial_number)
        suspicious = scans.filter(outcome_label__icontains="suspicious").count()
        prob = min(100, suspicious * 25)
    return _result(
        score=prob,
        confidence=70,
        reasons=[f"Serial {serial_number} risk assessment"],
        actions=["Quarantine unit", "Field verification"],
    )


def calculate_shortage_pressure(*, region_state: str = "") -> dict:
    score = 35
    reasons = ["Baseline supply chain monitoring"]
    if region_state:
        org_count = Organisation.objects.filter(state__iexact=region_state, is_active=True).count()
        score = min(100, max(20, 50 - org_count))
        reasons.append(f"{org_count} active organisations in {region_state}")
    return _result(score=score, confidence=55, reasons=reasons, actions=["Monitor shortage forecasts"])


def calculate_recall_execution_risk() -> dict:
    campaigns = RecallExecutionCampaign.objects.filter(status="active")
    pending = sum(max(0, c.pharmacies_targeted - c.pharmacies_acknowledged) for c in campaigns)
    score = min(100, pending * 5 + campaigns.count() * 10)
    return _result(
        score=score,
        confidence=75,
        reasons=[f"{campaigns.count()} active campaigns", f"{pending} pending pharmacy acks"],
        actions=["Escalate recall execution", "Notify regional regulators"],
    )
