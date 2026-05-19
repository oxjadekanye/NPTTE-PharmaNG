"""Deterministic risk breakdown aligned with Phase 18 scoring rules."""
from __future__ import annotations

from datetime import timedelta

from django.utils import timezone

from apps.intelligence.services.scoring import calculate_national_risk, calculate_regional_risk
from apps.organisations.models import Organisation
from apps.products.models import Product
from apps.scanning.models import ScanEvent
from apps.traceability.models import BatchRecall


def national_risk_breakdown() -> dict:
    since = timezone.now() - timedelta(hours=24)
    suspicious = ScanEvent.objects.filter(created_at__gte=since, outcome_label__icontains="suspicious").count()
    invalid = ScanEvent.objects.filter(created_at__gte=since, outcome_label__icontains="invalid").count()
    recalls = BatchRecall.objects.filter(effective_at__gte=since).count()
    risk = calculate_national_risk()
    contributions = [
        {
            "factor": "suspicious_scans_24h",
            "weight": 4,
            "count": suspicious,
            "contribution": min(100, suspicious * 4),
            "description": "Each suspicious scan adds up to 4 points toward national risk.",
        },
        {
            "factor": "invalid_serial_scans_24h",
            "weight": 3,
            "count": invalid,
            "contribution": min(100, invalid * 3),
            "description": "Invalid serial verification outcomes increase counterfeit exposure.",
        },
        {
            "factor": "recall_events_24h",
            "weight": 8,
            "count": recalls,
            "contribution": min(100, recalls * 8),
            "description": "Active recall events elevate national execution pressure.",
        },
        {
            "factor": "baseline_platform_load",
            "weight": None,
            "count": 1,
            "contribution": 15,
            "description": "Fixed baseline reflecting continuous national monitoring.",
        },
    ]
    thresholds = [
        {"name": "amber", "min_score": 40},
        {"name": "red", "min_score": 65},
        {"name": "critical", "min_score": 85},
    ]
    crossed = [t["name"] for t in thresholds if risk["score"] >= t["min_score"]]
    return {
        "score": risk["score"],
        "status": risk["status"],
        "confidence": risk["confidence"],
        "contributions": contributions,
        "thresholds_crossed": crossed,
        "reasons": risk["reasons"],
        "recommended_actions": risk["recommended_actions"],
    }


def regional_risk_breakdown(region_state: str) -> dict:
    risk = calculate_regional_risk(region_state=region_state)
    since = timezone.now() - timedelta(days=7)
    scans = ScanEvent.objects.filter(created_at__gte=since, organisation__state__iexact=region_state)
    total = scans.count()
    suspicious = scans.filter(outcome_label__icontains="suspicious").count()
    rate = (suspicious * 100 / total) if total else 0
    density_contribution = min(100, total // 5)
    rate_contribution = min(100, rate * 0.8)
    return {
        "region_state": region_state,
        "score": risk["score"],
        "status": risk["status"],
        "confidence": risk["confidence"],
        "contributions": [
            {"factor": "scan_density", "value": total, "contribution": density_contribution},
            {"factor": "suspicious_rate_pct", "value": round(rate, 1), "contribution": round(rate_contribution, 1)},
        ],
        "reasons": risk["reasons"],
        "recommended_actions": risk["recommended_actions"],
    }


def product_risk_breakdown(product: Product) -> dict:
    from apps.intelligence.services.scoring import calculate_product_risk

    risk = calculate_product_risk(product=product)
    return {
        "product_id": str(product.id),
        "score": risk["score"],
        "status": risk["status"],
        "confidence": risk["confidence"],
        "counterfeit_probability": risk.get("counterfeit_probability"),
        "reasons": risk["reasons"],
        "recommended_actions": risk["recommended_actions"],
    }


def organisation_risk_breakdown(organisation: Organisation) -> dict:
    from apps.intelligence.services.scoring import calculate_organisation_risk

    risk = calculate_organisation_risk(organisation=organisation)
    return {
        "organisation_id": str(organisation.id),
        "score": risk["score"],
        "status": risk["status"],
        "confidence": risk["confidence"],
        "reasons": risk["reasons"],
        "recommended_actions": risk["recommended_actions"],
    }
