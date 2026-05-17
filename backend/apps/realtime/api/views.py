"""SSE stream for live dashboard updates — additive, no WebSocket dependency."""
from __future__ import annotations

import json
import time

from django.http import StreamingHttpResponse
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.events.services import EventStreamService


class RealtimeStreamView(APIView):
    """
    Server-Sent Events endpoint for regulator dashboards.
    Polls event stream; Redis pub/sub ready when configured.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        category = request.query_params.get("category")
        since = int(request.query_params.get("since_sequence", 0))

        def event_generator():
            yield "event: connected\ndata: {}\n\n"
            last_seq = since
            for _ in range(60):
                events = EventStreamService.consume_event(
                    category=category,
                    since_sequence=last_seq,
                    limit=20,
                )
                for ev in events:
                    last_seq = max(last_seq, ev.get("sequence_number", 0))
                    yield f"data: {json.dumps({'type': 'event', 'payload': ev})}\n\n"
                yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': time.time()})}\n\n"
                time.sleep(5)

        response = StreamingHttpResponse(
            event_generator(),
            content_type="text/event-stream",
        )
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response
