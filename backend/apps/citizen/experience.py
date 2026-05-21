"""Phase 11 — advanced citizen public experience (demo-safe)."""
from __future__ import annotations

from django.utils import timezone

from apps.citizen.models import VerificationHistory
from apps.inventory.models import InventoryItem
from apps.products.models import Product


def verification_history(*, device_id: str | None = None, limit: int = 20) -> list[dict]:
    qs = VerificationHistory.objects.select_related("session").order_by("-verified_at")
    if device_id:
        qs = qs.filter(session__device_fingerprint=device_id)
    return [
        {
            "id": str(h.id),
            "serial_number": h.serial_number,
            "outcome": h.outcome,
            "verified_at": h.verified_at.isoformat(),
            "confidence_score": _confidence_from_outcome(h.outcome),
            "counterfeit_risk_explanation": _risk_explanation(h.outcome),
        }
        for h in qs[:limit]
    ]


def _risk_explanation(outcome: str) -> str:
    o = (outcome or "").lower()
    if "authentic" in o:
        return "Serial matches national traceability records with no active recall flags."
    if "recall" in o:
        return "Product is subject to an active national recall — do not use."
    if "suspicious" in o or "counterfeit" in o:
        return "Scan pattern inconsistent with expected supply chain custody."
    if "expired" in o:
        return "Batch expiry indicates product should not be dispensed."
    return "Outcome requires manual review at a reporting center."


def _confidence_from_outcome(outcome: str | None) -> int:
    if not outcome:
        return 50
    o = outcome.lower()
    if "authentic" in o:
        return 92
    if "recall" in o:
        return 15
    if "suspicious" in o or "counterfeit" in o:
        return 28
    if "expired" in o:
        return 40
    return 55


def medication_search(*, query: str, state: str = "") -> dict:
    products = Product.objects.filter(name__icontains=query).order_by("name")[:10]
    results = []
    for p in products:
        items = InventoryItem.objects.filter(product=p, is_active=True, quantity_on_hand__gt=0).select_related(
            "organisation"
        )[:5]
        pharmacies = [
            {
                "organisation_id": str(i.organisation_id),
                "organisation_name": i.organisation.name,
                "quantity": i.quantity_on_hand,
                "availability_status": i.availability_status,
            }
            for i in items
        ]
        results.append(
            {
                "product_id": str(p.id),
                "product_name": p.name,
                "nearest_pharmacies": pharmacies,
                "in_stock_nationally": len(pharmacies) > 0,
            }
        )
    return {
        "query": query,
        "state_filter": state,
        "results": results,
        "disclaimer": "Demo stock visibility — not live pharmacy connectivity.",
        "searched_at": timezone.now().isoformat(),
    }


def medicine_safety_guidance(*, product_name: str = "", outcome: str = "") -> dict:
    base = (
        "Verify packaging integrity, NAFDAC registration, and batch/expiry dates. "
        "Report suspicious products via the national counterfeit hotline."
    )
    if "recall" in outcome.lower():
        return {
            "guidance": f"{base} This product may be under active recall — do not use.",
            "risk_level": "high",
            "source": "deterministic_fallback",
        }
    if "suspicious" in outcome.lower():
        return {
            "guidance": f"{base} Do not purchase or consume until regulator confirmation.",
            "risk_level": "high",
            "source": "deterministic_fallback",
        }
    return {
        "guidance": f"{base} Product: {product_name or 'unknown'}.",
        "risk_level": "low" if "authentic" in outcome.lower() else "medium",
        "source": "deterministic_fallback",
    }


def public_safety_notices() -> list[dict]:
    return [
        {
            "id": "notice-recall-001",
            "title": "National recall monitoring active",
            "body": "Citizens should verify serials before purchase.",
            "priority": "high",
        },
        {
            "id": "notice-reporting-002",
            "title": "Report counterfeit medicines",
            "body": "Use in-app reporting or visit a NAFDAC reporting center.",
            "priority": "normal",
        },
    ]
