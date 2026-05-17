"""Cross-border pharmaceutical security services."""
from __future__ import annotations

from decimal import Decimal

from django.utils import timezone

from apps.international.models import ImportManifest, ImportRiskAssessment


def validate_import_manifest(*, manifest: ImportManifest) -> dict:
    """Customs verification and import risk scoring."""
    score = Decimal("0")
    indicators = []
    if not manifest.batch_references:
        score += Decimal("25")
        indicators.append("missing_batch_references")
    if len(manifest.origin_country) != 2:
        score += Decimal("15")
        indicators.append("invalid_origin_country")
    if manifest.batch_references and len(manifest.batch_references) > 50:
        score += Decimal("20")
        indicators.append("excessive_batch_volume")

    risk_score = min(score, Decimal("100"))
    ImportRiskAssessment.objects.update_or_create(
        manifest=manifest,
        defaults={
            "risk_score": risk_score,
            "suspicious_indicators": indicators,
            "assessed_at": timezone.now(),
        },
    )
    return {
        "manifest_number": manifest.manifest_number,
        "risk_score": str(risk_score),
        "indicators": indicators,
        "valid": risk_score < 70,
    }
