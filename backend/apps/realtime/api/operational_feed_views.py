"""Phase 11 — safe polling feed (additive to SSE stream)."""
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.roles import is_regulator_user
from apps.realtime.services.operational_feed import build_operational_feed
from apps.tenancy.services.tenant import get_active_organisation_id


class OperationalFeedPollingView(APIView):
    """
    Lightweight aggregated feed for dashboards and mobile.
    Clients poll with since_sequence; no WebSocket required.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            since = int(request.GET.get("since_sequence", 0))
        except (TypeError, ValueError):
            since = 0
        channels = [c.strip() for c in request.GET.get("channels", "").split(",") if c.strip()]
        org_id = request.GET.get("organisation_id")
        if not is_regulator_user(request.user) and not request.user.is_superuser:
            org_id = str(get_active_organisation_id(request) or org_id or "")
        payload = build_operational_feed(
            organisation_id=org_id or None,
            since_sequence=since,
            channels=channels or None,
            limit=int(request.GET.get("limit", 40)),
        )
        return api_response(data=payload, message="Operational feed")


class OperationalPrefetchView(APIView):
    """Screen prefetch hints — routes and cache keys for client warm-up."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return api_response(
            data={
                "routes": [
                    "/regulator/tasks",
                    "/regulator/alert-center",
                    "/executive/national-ops",
                    "/pharmacy/inventory",
                ],
                "poll_interval_ms": 15000,
                "sse_url": "/api/v1/realtime/stream/",
                "feed_url": "/api/v1/realtime/operational-feed/",
            },
            message="Prefetch manifest",
        )
