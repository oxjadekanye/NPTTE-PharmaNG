"""
Patient medication search services (Phase 1 placeholders).

Geospatial matching, inventory joins, and ranking will be implemented
in a dedicated phase with PostGIS or equivalent spatial indexing.
"""
from decimal import Decimal
from typing import Any

from apps.core.constants import AvailabilityStatus, MedicationSearchStatus
from apps.inventory.models import InventoryItem
from apps.organisations.models import Organisation
from apps.patients.models import MedicationSearchRequest
from apps.pharmacies.models import PharmacyProfile


def _haversine_miles(
    lat1: Decimal,
    lon1: Decimal,
    lat2: Decimal,
    lon2: Decimal,
) -> float:
    """
    Approximate distance in miles between two WGS84 points.

    Placeholder implementation for Phase 1; replace with PostGIS ST_DWithin
    for production scale and accuracy.
    """
    from math import asin, cos, radians, sin, sqrt

    lat1_f, lon1_f = float(lat1), float(lon1)
    lat2_f, lon2_f = float(lat2), float(lon2)
    dlat = radians(lat2_f - lat1_f)
    dlon = radians(lon2_f - lon1_f)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1_f)) * cos(radians(lat2_f)) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return 3958.8 * c  # Earth radius in miles


def find_pharmacies_with_stock(
    *,
    product_id,
    latitude: Decimal,
    longitude: Decimal,
    radius_miles: Decimal,
) -> list[dict[str, Any]]:
    """
    Return pharmacies within radius that report in-stock inventory for a product.

    Phase 1: Python-side filtering over queryset. Phase 2+: database spatial query.
    """
    inventory_qs = (
        InventoryItem.objects.filter(
            product_id=product_id,
            is_active=True,
            availability_status=AvailabilityStatus.IN_STOCK,
            quantity_on_hand__gt=0,
        )
        .select_related("organisation")
        .prefetch_related("organisation__pharmacy_profile")
    )

    matches: list[dict[str, Any]] = []
    radius = float(radius_miles)

    for item in inventory_qs:
        org: Organisation = item.organisation
        if org.latitude is None or org.longitude is None:
            continue
        if not PharmacyProfile.objects.filter(organisation=org, is_active=True).exists():
            continue

        distance = _haversine_miles(latitude, longitude, org.latitude, org.longitude)
        if distance <= radius:
            matches.append(
                {
                    "organisation_id": str(org.id),
                    "legal_name": org.legal_name,
                    "distance_miles": round(distance, 2),
                    "quantity_on_hand": item.quantity_on_hand,
                    "availability_status": item.availability_status,
                }
            )

    matches.sort(key=lambda m: m["distance_miles"])
    return matches


def process_medication_search(search_request: MedicationSearchRequest) -> MedicationSearchRequest:
    """
    Execute a medication search request and persist results snapshot.

    Called by API layer or async workers in later phases.
    """
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
