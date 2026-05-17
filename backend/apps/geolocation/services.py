"""Geolocation utilities — PostGIS-ready distance calculations."""
from __future__ import annotations

from decimal import Decimal


def haversine_km(lat1: Decimal, lon1: Decimal, lat2: Decimal, lon2: Decimal) -> float:
    from math import asin, cos, radians, sin, sqrt

    lat1_f, lon1_f = float(lat1), float(lon1)
    lat2_f, lon2_f = float(lat2), float(lon2)
    dlat = radians(lat2_f - lat1_f)
    dlon = radians(lon2_f - lon1_f)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1_f)) * cos(radians(lat2_f)) * sin(dlon / 2) ** 2
    return 6371.0 * 2 * asin(sqrt(a))


def miles_to_km(miles: Decimal) -> float:
    return float(miles) * 1.60934
