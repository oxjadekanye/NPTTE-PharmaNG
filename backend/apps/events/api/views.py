from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.permissions import IsRegulatorUser
from apps.events.services import EventStreamService


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
