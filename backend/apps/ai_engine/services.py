"""AI pharmaceutical intelligence — heuristic engines (ML-ready)."""
from __future__ import annotations

from decimal import Decimal

from apps.ai_engine.models import (
    AIRiskSignal,
    CounterfeitRiskAssessment,
    DemandForecast,
    InventoryPrediction,
    OrganisationRiskScore,
)
from apps.core.constants import RiskLevel
from apps.inventory.models import InventoryItem
from apps.organisations.models import Organisation
from apps.products.models import Product
from apps.verification.models import VerificationScanLog


def calculate_counterfeit_probability(*, serial_number: str) -> Decimal:
    failures = VerificationScanLog.objects.filter(serial_number=serial_number).exclude(
        outcome="authentic"
    ).count()
    prob = Decimal(min(failures * 15, 95))
    level = RiskLevel.LOW
    if prob >= 70:
        level = RiskLevel.HIGH
    elif prob >= 40:
        level = RiskLevel.MEDIUM
    CounterfeitRiskAssessment.objects.create(
        serial_number=serial_number,
        probability=prob,
        risk_level=level,
        factors={"failed_scans": failures},
    )
    return prob


def calculate_shortage_probability(*, organisation: Organisation, product: Product) -> Decimal:
    item = InventoryItem.objects.filter(organisation=organisation, product=product, is_active=True).first()
    if not item:
        prob = Decimal("90")
    elif item.quantity_on_hand <= 5:
        prob = Decimal("75")
    elif item.quantity_on_hand <= 20:
        prob = Decimal("45")
    else:
        prob = Decimal("10")
    InventoryPrediction.objects.update_or_create(
        organisation=organisation,
        product=product,
        defaults={
            "predicted_stock_days_remaining": max(item.quantity_on_hand // 2, 0) if item else 0,
            "shortage_probability": prob,
        },
    )
    return prob


def calculate_diversion_risk(*, organisation: Organisation) -> Decimal:
    from apps.traceability.models import SupplyChainTransaction

    velocity = SupplyChainTransaction.objects.filter(
        source_organisation=organisation
    ).count()
    score = Decimal(min(velocity / 10, 100))
    OrganisationRiskScore.objects.update_or_create(
        organisation=organisation,
        defaults={"diversion_score": score, "overall_score": score},
    )
    AIRiskSignal.objects.create(
        signal_type="diversion_risk",
        organisation=organisation,
        score=score,
        evidence={"transaction_velocity": velocity},
    )
    return score


def calculate_national_risk_score() -> Decimal:
    from django.db.models import Avg
    from django.utils import timezone

    from apps.ai_engine.models import NationalRiskSignal

    org_scores = OrganisationRiskScore.objects.aggregate(avg=Avg("overall_score"))
    counterfeit = VerificationScanLog.objects.exclude(outcome="authentic").count()
    national = Decimal(min((org_scores["avg"] or 0) + counterfeit, 100))
    NationalRiskSignal.objects.create(
        signal_type="national_rollup",
        national_score=national,
        recorded_at=timezone.now(),
        regional_data={"counterfeit_signals": counterfeit},
    )
    return national


def predict_regional_shortage(*, product: Product, state: str) -> Decimal:
    from django.utils import timezone

    from apps.ai_engine.models import ShortageForecast

    prob = calculate_shortage_probability(
        organisation=Organisation.objects.filter(state=state).first() or Organisation.objects.first(),
        product=product,
    )
    ShortageForecast.objects.create(
        product=product,
        state=state,
        forecast_date=timezone.now().date(),
        shortage_probability=prob,
    )
    return prob


def detect_diversion_patterns(*, organisation: Organisation) -> Decimal:
    from django.utils import timezone

    from apps.ai_engine.models import DiversionProbability, MedicineMovementPattern
    from apps.traceability.models import SupplyChainTransaction

    txs = SupplyChainTransaction.objects.filter(source_organisation=organisation).count()
    prob = Decimal(min(txs / 5, 100))
    DiversionProbability.objects.update_or_create(
        organisation=organisation,
        defaults={"probability": prob, "factors": {"tx_count": txs}},
    )
    if prob > 50 and Product.objects.exists():
        now = timezone.now()
        MedicineMovementPattern.objects.create(
            product=Product.objects.first(),
            origin_state=organisation.state or "Unknown",
            destination_state="Unknown",
            movement_volume=txs,
            anomaly_score=prob,
            period_start=now,
            period_end=now,
        )
    return prob
