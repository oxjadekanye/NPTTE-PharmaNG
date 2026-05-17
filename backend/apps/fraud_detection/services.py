"""Fraud risk scoring service (rule-based foundation for future ML)."""
from __future__ import annotations

from decimal import Decimal

from apps.core.constants import RiskLevel
from apps.fraud_detection.models import FraudRiskFlag


def score_inventory_anomaly(*, organisation, quantity_delta: int, threshold: int = 500) -> Decimal:
    """Rule-based risk score for abnormal inventory movements."""
    if abs(quantity_delta) >= threshold:
        return Decimal("85.0")
    if abs(quantity_delta) >= threshold // 2:
        return Decimal("55.0")
    return Decimal("10.0")


def create_fraud_flag(
    *,
    flag_type: str,
    organisation=None,
    supply_chain_transaction=None,
    risk_score: Decimal,
    description: str = "",
) -> FraudRiskFlag:
    risk_level = RiskLevel.LOW
    if risk_score >= 80:
        risk_level = RiskLevel.CRITICAL
    elif risk_score >= 60:
        risk_level = RiskLevel.HIGH
    elif risk_score >= 35:
        risk_level = RiskLevel.MEDIUM

    return FraudRiskFlag.objects.create(
        flag_type=flag_type,
        organisation=organisation,
        supply_chain_transaction=supply_chain_transaction,
        risk_score=risk_score,
        risk_level=risk_level,
        description=description,
    )
