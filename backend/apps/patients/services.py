"""
Patient medication search services.
"""
from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Any
from zoneinfo import ZoneInfo

from django.db.models import Q
from django.utils import timezone

from apps.core.constants import AvailabilityStatus, MedicationSearchStatus
from apps.inventory.models import InventoryItem
from apps.organisations.models import Organisation
from apps.patients.models import MedicationSearchRequest
from apps.pharmacies.models import PharmacyProfile
from apps.products.models import Product

LAGOS_TZ = ZoneInfo("Africa/Lagos")


def _haversine_miles(
    lat1: Decimal,
    lon1: Decimal,
    lat2: Decimal,
    lon2: Decimal,
) -> float:
    from math import asin, cos, radians, sin, sqrt

    lat1_f, lon1_f = float(lat1), float(lon1)
    lat2_f, lon2_f = float(lat2), float(lon2)
    dlat = radians(lat2_f - lat1_f)
    dlon = radians(lon2_f - lon1_f)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1_f)) * cos(radians(lat2_f)) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return 3958.8 * c


def _format_address(org: Organisation) -> str:
    parts = [
        org.address_line_1,
        org.address_line_2,
        org.city,
        org.state,
        org.country,
    ]
    return ", ".join(p for p in parts if p)


def _opening_status(opening_hours: dict) -> str:
    """Derive open/closed/unknown from weekly opening_hours JSON."""
    if not opening_hours:
        return "unknown"
    now = timezone.now().astimezone(LAGOS_TZ)
    day_key = now.strftime("%A").lower()
    day_hours = opening_hours.get(day_key) or opening_hours.get(day_key[:3])
    if not day_hours:
        return "unknown"
    if day_hours.get("closed"):
        return "closed"
    open_str = day_hours.get("open")
    close_str = day_hours.get("close")
    if not open_str or not close_str:
        return "unknown"
    try:
        open_time = datetime.strptime(open_str, "%H:%M").time()
        close_time = datetime.strptime(close_str, "%H:%M").time()
        current = now.time()
        if open_time <= current <= close_time:
            return "open"
        return "closed"
    except ValueError:
        return "unknown"


def search_products(
    *,
    query: str = "",
    medicine_name: str = "",
    dosage: str = "",
    formulation: str = "",
    generic_name: str = "",
    brand_name: str = "",
) -> list[Product]:
    """Resolve products by multi-field text search."""
    qs = Product.objects.filter(is_active=True, status="active")
    terms = [t for t in [query, medicine_name, generic_name, brand_name] if t]
    if terms:
        q_obj = Q()
        for term in terms:
            q_obj |= (
                Q(name__icontains=term)
                | Q(brand_name__icontains=term)
                | Q(active_ingredient__icontains=term)
            )
        qs = qs.filter(q_obj)
    if dosage:
        qs = qs.filter(strength__icontains=dosage)
    if formulation:
        qs = qs.filter(dosage_form__icontains=formulation)
    return list(qs.distinct()[:50])


def build_pharmacy_match(item: InventoryItem, distance: float) -> dict[str, Any]:
    org: Organisation = item.organisation
    profile = getattr(org, "pharmacy_profile", None)
    opening_hours = profile.opening_hours if profile else {}
    return {
        "pharmacy_id": str(profile.id) if profile else None,
        "organisation_id": str(org.id),
        "pharmacy_name": org.trading_name or org.legal_name,
        "address": _format_address(org),
        "city": org.city,
        "state": org.state,
        "phone_number": org.phone_number,
        "distance_miles": round(distance, 2),
        "quantity_available": item.quantity_on_hand,
        "availability_status": item.availability_status,
        "opening_status": _opening_status(opening_hours),
        "opening_hours": opening_hours,
        "latitude": str(org.latitude) if org.latitude is not None else None,
        "longitude": str(org.longitude) if org.longitude is not None else None,
        "product_id": str(item.product_id),
        "product_name": item.product.name,
        "brand_name": item.product.brand_name,
        "strength": item.product.strength,
        "dosage_form": item.product.dosage_form,
    }


def find_pharmacies_with_stock(
    *,
    product_id=None,
    latitude: Decimal,
    longitude: Decimal,
    radius_miles: Decimal,
    product_ids: list | None = None,
) -> list[dict[str, Any]]:
    """Return pharmacies within radius with in-stock inventory."""
    ids = product_ids or ([product_id] if product_id else [])
    if not ids:
        return []

    inventory_qs = (
        InventoryItem.objects.filter(
            product_id__in=ids,
            is_active=True,
            availability_status=AvailabilityStatus.IN_STOCK,
            quantity_on_hand__gt=0,
        )
        .select_related("organisation", "product")
        .prefetch_related("organisation__pharmacy_profile")
    )

    matches: list[dict[str, Any]] = []
    radius = float(radius_miles)
    seen_orgs: set[str] = set()

    for item in inventory_qs:
        org: Organisation = item.organisation
        org_key = str(org.id)
        if org.latitude is None or org.longitude is None:
            continue
        if not PharmacyProfile.objects.filter(organisation=org, is_active=True).exists():
            continue

        distance = _haversine_miles(latitude, longitude, org.latitude, org.longitude)
        if distance > radius:
            continue

        match = build_pharmacy_match(item, distance)
        if org_key in seen_orgs:
            continue
        seen_orgs.add(org_key)
        matches.append(match)

    matches.sort(key=lambda m: m["distance_miles"])
    return matches


def run_medication_search(
    *,
    latitude: Decimal,
    longitude: Decimal,
    radius_miles: Decimal,
    patient=None,
    product_id=None,
    search_term: str = "",
    medicine_name: str = "",
    dosage: str = "",
    formulation: str = "",
    generic_name: str = "",
    brand_name: str = "",
) -> tuple[MedicationSearchRequest | None, list[dict[str, Any]], list[Product]]:
    """
    Execute medication search across product catalogue and pharmacy inventory.

    Returns (search_request, pharmacy_matches, matched_products).
    """
    products = search_products(
        query=search_term,
        medicine_name=medicine_name,
        dosage=dosage,
        formulation=formulation,
        generic_name=generic_name,
        brand_name=brand_name,
    )
    if product_id:
        products = list(Product.objects.filter(id=product_id, is_active=True)) or products

    if not products:
        return None, [], []

    product_ids = [p.id for p in products]
    primary_product = products[0]

    search_request = MedicationSearchRequest.objects.create(
        patient=patient,
        product=primary_product,
        search_term=search_term or medicine_name or generic_name or brand_name,
        latitude=latitude,
        longitude=longitude,
        radius_miles=radius_miles,
        search_status=MedicationSearchStatus.PROCESSING,
    )

    try:
        results = find_pharmacies_with_stock(
            product_ids=product_ids,
            latitude=latitude,
            longitude=longitude,
            radius_miles=radius_miles,
        )
        search_request.results_snapshot = results
        search_request.result_count = len(results)
        search_request.search_status = MedicationSearchStatus.COMPLETED
    except Exception:
        search_request.search_status = MedicationSearchStatus.FAILED
        raise
    finally:
        search_request.save(
            update_fields=[
                "results_snapshot",
                "result_count",
                "search_status",
                "updated_at",
            ]
        )

    return search_request, results, products


def process_medication_search(search_request: MedicationSearchRequest) -> MedicationSearchRequest:
    """Process an existing search request record."""
    search_request.search_status = MedicationSearchStatus.PROCESSING
    search_request.save(update_fields=["search_status", "updated_at"])

    try:
        results = find_pharmacies_with_stock(
            product_id=search_request.product_id,
            latitude=search_request.latitude,
            longitude=search_request.longitude,
            radius_miles=search_request.radius_miles,
        )
        search_request.results_snapshot = results
        search_request.result_count = len(results)
        search_request.search_status = MedicationSearchStatus.COMPLETED
    except Exception:
        search_request.search_status = MedicationSearchStatus.FAILED
        raise
    finally:
        search_request.save(
            update_fields=[
                "results_snapshot",
                "result_count",
                "search_status",
                "updated_at",
            ]
        )

    return search_request
