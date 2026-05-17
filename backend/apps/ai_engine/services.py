"""AI engine service stubs — async/ML integration points."""
from __future__ import annotations

from decimal import Decimal

from apps.ai_engine.models import AIRiskAssessment
from apps.core.constants import RiskLevel


def assess_counterfeit_risk(*, organisation=None, transaction_count: int = 0) -> AIRiskAssessment:
    """Rule-based counterfeit risk placeholder for future ML."""
    score = Decimal(min(transaction_count * 2, 95))
    level = RiskLevel.LOW
    if score >= 70:
        level = RiskLevel.HIGH
    elif score >= 40:
        level = RiskLevel.MEDIUM
    return AIRiskAssessment.objects.create(
        assessment_type="counterfeit_prediction",
        organisation=organisation,
        risk_score=score,
        risk_level=level,
        model_version="rules-v1",
        input_features={"transaction_count": transaction_count},
        output_explanation={"method": "heuristic", "note": "ML integration pending"},
    )


def assess_shortage_risk(*, state: str, stock_ratio: float) -> AIRiskAssessment:
    score = Decimal(max(0, min(100, (1 - stock_ratio) * 100)))
    level = RiskLevel.HIGH if score >= 70 else RiskLevel.MEDIUM if score >= 40 else RiskLevel.LOW
    return AIRiskAssessment.objects.create(
        assessment_type="shortage_prediction",
        risk_score=score,
        risk_level=level,
        model_version="rules-v1",
        input_features={"state": state, "stock_ratio": stock_ratio},
        output_explanation={"method": "heuristic"},
    )
