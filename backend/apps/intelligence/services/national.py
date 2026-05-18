"""Persist intelligence snapshots and profiles."""
from __future__ import annotations

from apps.intelligence.models import (
    NationalRiskSnapshot,
    OrganisationRiskProfile,
    ProductRiskProfile,
    RegionalRiskProfile,
)
from apps.intelligence.services.scoring import (
    calculate_national_risk,
    calculate_organisation_risk,
    calculate_product_risk,
    calculate_regional_risk,
)
from apps.organisations.models import Organisation
from apps.products.models import Product


def refresh_national_snapshot() -> NationalRiskSnapshot:
    risk = calculate_national_risk()
    return NationalRiskSnapshot.objects.create(
        national_score=risk["score"],
        status=risk["status"],
        confidence=risk["confidence"],
        reasons=risk["reasons"],
        recommended_actions=risk["recommended_actions"],
        metrics=risk,
    )


def refresh_organisation_profile(organisation: Organisation) -> OrganisationRiskProfile:
    risk = calculate_organisation_risk(organisation=organisation)
    return OrganisationRiskProfile.objects.create(
        organisation=organisation,
        score=risk["score"],
        status=risk["status"],
        confidence=risk["confidence"],
        integrity_score=max(0, 100 - risk["score"]),
        reasons=risk["reasons"],
        recommended_actions=risk["recommended_actions"],
    )


def refresh_product_profile(product: Product) -> ProductRiskProfile:
    risk = calculate_product_risk(product=product)
    return ProductRiskProfile.objects.create(
        product=product,
        score=risk["score"],
        status=risk["status"],
        confidence=risk["confidence"],
        counterfeit_probability=risk.get("counterfeit_probability", 0),
        reasons=risk["reasons"],
        recommended_actions=risk["recommended_actions"],
    )


def refresh_regional_profile(region_state: str) -> RegionalRiskProfile:
    risk = calculate_regional_risk(region_state=region_state)
    return RegionalRiskProfile.objects.create(
        region_state=region_state,
        score=risk["score"],
        status=risk["status"],
        confidence=risk["confidence"],
        scan_density=risk.get("scan_density", 0),
        suspicious_count=0,
        reasons=risk["reasons"],
        recommended_actions=risk["recommended_actions"],
    )
