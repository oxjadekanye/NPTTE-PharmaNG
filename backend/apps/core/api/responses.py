"""Standardized API response envelope for NPTTE clients."""
from __future__ import annotations
from rest_framework.response import Response


def api_response(
    *,
    data=None,
    message: str = "Success",
    status_code: int = 200,
    meta: dict | None = None,
):
    """Return a consistent JSON structure across national platform APIs."""
    payload = {
        "success": 200 <= status_code < 300,
        "message": message,
        "data": data,
    }
    if meta:
        payload["meta"] = meta
    return Response(payload, status=status_code)
