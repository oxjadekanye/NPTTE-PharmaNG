"""Phase 12 — national medicine & manufacturer intelligence (demo-safe heuristics)."""
from __future__ import annotations

from django.db.models import Count, Q
from django.utils import timezone

from apps.core.constants import AvailabilityStatus
from apps.inventory.models import InventoryItem
from apps.intelligence.models import ProductRiskProfile
from apps.organisations.models import Organisation
from apps.products.models import Product
from apps.scanning.models import ScanEvent

# Demo watchlist — additive national monitoring list
BLACKLIST_WATCHLIST = [
    {"code": "DEMO-BL-001", "name": "Unregistered antimalarial combo", "reason": "NAFDAC alert reference"},
    {"code": "DEMO-BL-002", "name": "Counterfeit insulin batch pattern", "reason": "Cluster investigation"},
]


def _shortage_sensitivity(product: Product) -> int:
    low = InventoryItem.objects.filter(
        product=product,
        availability_status__in=(AvailabilityStatus.LOW_STOCK, AvailabilityStatus.OUT_OF_STOCK),
    ).count()
    return min(100, 20 + low * 15)


def _cold_chain_sensitive(product: Product) -> bool:
    name = (product.name or "").lower() + (product.active_ingredient or "").lower()
    return any(k in name for k in ("insulin", "vaccine", "cold", "biologic"))


def _medicine_profile(product: Product, risk: ProductRiskProfile | None = None) -> dict:
    risk = risk or ProductRiskProfile.objects.filter(product=product).order_by("-created_at").first()
    counterfeit = float(risk.counterfeit_probability) if risk else 25.0
    shortage = _shortage_sensitivity(product)
    return {
        "id": str(product.id),
        "name": product.name,
        "brand_name": product.brand_name,
        "active_ingredient": product.active_ingredient,
        "national_product_code": product.national_product_code,
        "manufacturer_id": str(product.manufacturer_id) if product.manufacturer_id else None,
        "risk_classification": risk.status if risk else "amber",
        "counterfeit_vulnerability_score": int(counterfeit),
        "shortage_sensitivity_score": shortage,
        "cold_chain_sensitive": _cold_chain_sensitive(product),
        "import_dependency_index": 55 if not product.manufacturer_id else 35,
        "on_blacklist_watchlist": product.national_product_code in {b["code"] for b in BLACKLIST_WATCHLIST},
    }


def list_medicine_intelligence(*, query: str = "", limit: int = 50) -> list[dict]:
    qs = Product.objects.all().order_by("name")
    if query:
        qs = qs.filter(Q(name__icontains=query) | Q(active_ingredient__icontains=query))
    profiles = []
    for p in qs[:limit]:
        profiles.append(_medicine_profile(p))
    return profiles


def get_medicine_intelligence(product_id) -> dict | None:
    product = Product.objects.filter(pk=product_id).select_related("manufacturer").first()
    if not product:
        return None
    risk = ProductRiskProfile.objects.filter(product=product).order_by("-created_at").first()
    suspicious = ScanEvent.objects.filter(outcome_label__icontains="suspicious").count()
    scans = ScanEvent.objects.count()
    profile = _medicine_profile(product, risk)
    profile.update(
        {
            "dosage_guidance": product.dosage_guidance,
            "reference_price": str(product.reference_price) if product.reference_price else None,
            "scan_volume": scans,
            "suspicious_scan_signals": suspicious,
            "recommended_actions": (risk.recommended_actions if risk else [])
            or ["Monitor dispensing in high-risk states", "Verify batch certificates at border"],
            "blacklist_watchlist": BLACKLIST_WATCHLIST,
            "disclaimer": "National intelligence profile — demo operational data.",
        }
    )
    return profile


def list_manufacturer_intelligence(*, limit: int = 30) -> list[dict]:
    orgs = (
        Organisation.objects.filter(manufactured_products__isnull=False)
        .distinct()
        .annotate(product_count=Count("manufactured_products"))[:limit]
    )
    rows = []
    for org in orgs:
        suspicious = ScanEvent.objects.filter(organisation=org, outcome_label__icontains="suspicious").count()
        rows.append(
            {
                "id": str(org.id),
                "name": org.name,
                "state": org.state,
                "product_count": org.product_count,
                "suspicious_manufacturer_indicator": suspicious > 2,
                "suspicious_scan_count": suspicious,
                "compliance_score": max(40, 95 - suspicious * 8),
            }
        )
    return rows


def national_shortage_risk() -> dict:
    low = InventoryItem.objects.filter(
        Q(availability_status=AvailabilityStatus.LOW_STOCK)
        | Q(availability_status=AvailabilityStatus.OUT_OF_STOCK)
    ).count()
    total = max(InventoryItem.objects.filter(is_active=True).count(), 1)
    index = min(100, int(30 + (low / total) * 70))
    products = (
        InventoryItem.objects.filter(availability_status=AvailabilityStatus.LOW_STOCK)
        .select_related("product")[:10]
    )
    return {
        "shortage_risk_index": index,
        "low_stock_skus": low,
        "at_risk_products": [
            {"product_id": str(i.product_id), "name": i.product.name, "quantity": i.quantity_on_hand}
            for i in products
        ],
        "forecast_note": "Elevated risk in northern corridors for cold-chain biologics (deterministic).",
        "computed_at": timezone.now().isoformat(),
    }


def national_counterfeit_risk() -> dict:
    total = max(ScanEvent.objects.count(), 1)
    suspicious = ScanEvent.objects.filter(outcome_label__icontains="suspicious").count()
    heat = min(100, int(25 + (suspicious / total) * 75))
    dupes = (
        ScanEvent.objects.values("serial_number")
        .annotate(c=Count("id"))
        .filter(c__gt=1)
        .count()
    )
    return {
        "counterfeit_heat_score": heat,
        "suspicious_scan_rate": round(suspicious / total, 4),
        "duplicate_serial_clusters": dupes,
        "hotspot_states": ["Lagos", "Kano", "Onitsha"],
        "computed_at": timezone.now().isoformat(),
    }
