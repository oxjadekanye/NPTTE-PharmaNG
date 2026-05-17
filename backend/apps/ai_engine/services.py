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
