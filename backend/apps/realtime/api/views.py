"""SSE stream for live dashboard updates — tenant-scoped, Channels-ready abstraction."""
from __future__ import annotations

import json
import time

from django.http import StreamingHttpResponse
from django.views import View

from apps.core.roles import is_regulator_user
from apps.events.services import EventStreamService
from apps.streambus.services.telemetry import aggregate_telemetry
from apps.tenancy.services.tenant import get_active_organisation_id


def _resolve_user(request):
    token = request.GET.get("token") or ""
    auth = request.META.get("HTTP_AUTHORIZATION", "")
    if auth.startswith("Bearer "):
        token = auth[7:]
    if not token:
        return getattr(request, "user", None) if getattr(request, "user", None).is_authenticated else None
    try:
        from rest_framework_simplejwt.tokens import AccessToken
        from django.contrib.auth import get_user_model

        validated = AccessToken(token)
        return get_user_model().objects.filter(pk=validated["user_id"]).first()
    except Exception:
        return None


class RealtimeStreamView(View):
    """
    Server-Sent Events for regulator and organisation-scoped live feeds.
    WebSocket-ready: same event envelope can fan out via Channels later.
    """

    def get(self, request):
        user = _resolve_user(request)
        category = request.GET.get("category")
        channel = request.GET.get("channel")
        include_patches = request.GET.get("patches", "1") in ("1", "true", "yes")
        try:
            since = int(request.GET.get("since_sequence", 0))
        except (TypeError, ValueError):
            since = 0

        organisation_id = request.GET.get("organisation_id")
        if user and user.is_authenticated:
            if not is_regulator_user(user) and not user.is_superuser:
                organisation_id = str(user.organisation_id or request.GET.get("organisation_id") or "")

        def event_generator():
            yield "event: connected\ndata: {}\n\n"
            last_seq = since
            batch_count = 0
            for tick in range(60):
                events = EventStreamService.consume_event(
                    category=category,
                    organisation_id=organisation_id or None,
                    since_sequence=last_seq,
                    limit=20,
                )
                if events:
                    batch_count += len(events)
                    for ev in events:
                        if channel:
                            payload = ev.get("payload") if isinstance(ev.get("payload"), dict) else {}
                            ev_channel = payload.get("stream_channel") or "national"
                            if ev_channel != channel:
                                continue
                        last_seq = max(last_seq, ev.get("sequence_number", 0))
                        yield f"data: {json.dumps({'type': 'event', 'payload': ev})}\n\n"
                        if include_patches:
                            payload = ev.get("payload") if isinstance(ev.get("payload"), dict) else ev
                            patch = payload.get("patch") if isinstance(payload, dict) else None
                            if not patch and isinstance(payload, dict):
                                from apps.command_orchestration.services.patches import build_event_patch

                                patch = build_event_patch(
                                    event_type=str(ev.get("event_type") or payload.get("event_type", "")),
                                    payload=payload,
                                )
                            if patch:
                                yield f"data: {json.dumps({'type': 'patch', 'payload': patch})}\n\n"
                if tick % 6 == 0 and tick > 0:
                    try:
                        snap = aggregate_telemetry(organisation=None, window_seconds=300)
                        yield f"data: {json.dumps({'type': 'telemetry', 'payload': {'scan_throughput': snap.scan_throughput, 'event_throughput': snap.event_throughput, 'suspicious_rate': float(snap.suspicious_rate)}})}\n\n"
                    except Exception:
                        pass
                yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': time.time(), 'batch_events': batch_count})}\n\n"
                time.sleep(5)

        response = StreamingHttpResponse(event_generator(), content_type="text/event-stream")
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response


class RealtimeWebSocketInfoView(View):
    """Channels-ready metadata — clients use SSE until WebSocket layer is enabled."""

    def get(self, request):
        from django.http import JsonResponse

        return JsonResponse(
            {
                "transport": "sse",
                "websocket_ready": True,
                "stream_url": "/api/v1/realtime/stream/",
                "note": "Django Channels can replace SSE without API contract changes",
            }
        )
