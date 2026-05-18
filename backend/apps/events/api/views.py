from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.permissions import IsRegulatorUser
from apps.events.services import EventStreamService


class NationalOperationsSummaryView(APIView):
    """
    Phase 9 — additive read-only aggregate for national ecosystem dashboards.
    Does not replace SSE or events replay; provides a stable JSON snapshot for UIs.
    """

    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        events = EventStreamService.consume_event(limit=50)
        data = {
            "national_threat_index": 62,
            "verifications_24h_roll": 184293,
            "active_recalls": 4,
            "customs_holds_open": 3,
            "warehouse_inspections_scheduled": 6,
            "shortage_watch_states": ["Enugu", "Lagos", "Kano"],
            "recent_event_sample": events[:12],
            "generated_at": timezone.now().isoformat(),
            "note": "Snapshot includes live event sample tail; scalar KPIs are presentation defaults unless wired to analytics.",
        }
        return api_response(data=data, message="National operations summary")


class EventReplayView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        since = int(request.query_params.get("since_sequence", 0))
        category = request.query_params.get("category")
        org_id = request.query_params.get("organisation_id")
        events = EventStreamService.consume_event(
            category=category,
            organisation_id=org_id,
            since_sequence=since,
            limit=int(request.query_params.get("limit", 100)),
        )
        return api_response(data={"events": events, "count": len(events)})
