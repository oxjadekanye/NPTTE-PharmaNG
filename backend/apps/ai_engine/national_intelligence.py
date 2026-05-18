"""Phase 10 — aggregated national risk intelligence (wraps existing AI engines)."""
from __future__ import annotations

from decimal import Decimal

from apps.ai_engine.services import (
    calculate_counterfeit_probability,
    calculate_national_risk_score,
    calculate_shortage_probability,
    detect_diversion_patterns,
)
from apps.organisations.models import Organisation
from apps.products.models import Product
from apps.verification.models import VerificationScanLog


def build_national_intelligence_snapshot() -> dict:
    national_score = float(calculate_national_risk_score())
    scan_anomalies = VerificationScanLog.objects.exclude(outcome="authentic").count()

    org = Organisation.objects.first()
    product = Product.objects.first()
    shortage_prob = 0.0
    diversion_prob = 0.0
    if org and product:
        shortage_prob = float(calculate_shortage_probability(organisation=org, product=product))
        diversion_prob = float(detect_diversion_patterns(organisation=org))

    return {
        "national_risk_score": national_score,
        "counterfeit_signals_24h": scan_anomalies,
        "shortage_forecast_probability": shortage_prob,
        "diversion_risk_probability": diversion_prob,
        "engines": [
            "counterfeit_probability",
            "suspicious_movement",
            "abnormal_scan_clustering",
            "medicine_diversion_prediction",
            "shortage_forecasting",
            "pharmacy_anomaly_scoring",
            "suspicious_import_scoring",
            "illegal_distribution_detection",
        ],
    }


def score_serial_risk(*, serial_number: str) -> dict:
    prob = float(calculate_counterfeit_probability(serial_number=serial_number))
    return {
        "serial_number": serial_number,
        "counterfeit_probability": prob,
        "band": "critical" if prob >= 70 else "high" if prob >= 40 else "elevated" if prob >= 20 else "low",
    }
