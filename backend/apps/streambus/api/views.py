"""Phase 17 — event bus and telemetry APIs."""
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.permissions import IsRegulatorUser
from apps.core.roles import is_regulator_user
from apps.streambus.models import (
    DeferredProcessingTask,
    EventEscalation,
    EventLifecycleLog,
    OperationalTelemetrySnapshot,
)
from apps.streambus.services.bus import OperationalEventBus, publish_operational_event
from apps.streambus.services.telemetry import aggregate_telemetry
from apps.tenancy.services.tenant import get_active_organisation_id, user_can_access_organisation


class EventPublishView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        org_id = request.data.get("organisation_id") or get_active_organisation_id(request)
        if org_id and not user_can_access_organisation(request.user, org_id):
            return api_response(message="Access denied", status_code=403)
        event = publish_operational_event(
            event_type=request.data.get("event_type", "organisation.action"),
            payload=request.data.get("payload", {}),
            organisation_id=org_id,
            severity=request.data.get("severity", "INFO"),
        )
        return api_response(data=event, message="Event published", status_code=201)


class EventReplayView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        since = int(request.query_params.get("since_sequence", 0))
        limit = int(request.query_params.get("limit", 100))
        category = request.query_params.get("category")
        org_id = request.query_params.get("organisation_id")
        if not is_regulator_user(request.user) and not request.user.is_superuser:
            org_id = str(get_active_organisation_id(request) or "")
            if not org_id:
                return api_response(data={"events": [], "count": 0}, message="No organisation context")
        events = OperationalEventBus.replay(
            organisation_id=org_id or None,
            since_sequence=since,
            limit=limit,
            category=category,
        )
        return api_response(data={"events": events, "count": len(events)}, message="Event replay")


class EventAcknowledgeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, event_id):
        ok = OperationalEventBus.acknowledge(event_id=event_id, actor=request.user)
        return api_response(data={"acknowledged": ok}, message="Event acknowledged")


class TelemetryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.organisations.models import Organisation

        org_id = request.query_params.get("organisation_id") or get_active_organisation_id(request)
        organisation = Organisation.objects.filter(pk=org_id).first() if org_id else None
        if organisation and not user_can_access_organisation(request.user, organisation.id):
            if not is_regulator_user(request.user):
                return api_response(message="Access denied", status_code=403)
        snaps = OperationalTelemetrySnapshot.objects.order_by("-created_at")
        if organisation:
            snaps = snaps.filter(organisation=organisation)
        elif not is_regulator_user(request.user):
            snaps = snaps.none()
        rows = [
            {
                "id": str(s.id),
                "scan_throughput": s.scan_throughput,
                "event_throughput": s.event_throughput,
                "suspicious_rate": float(s.suspicious_rate),
                "metrics": s.metrics,
                "created_at": s.created_at.isoformat(),
            }
            for s in snaps[:20]
        ]
        return api_response(data={"telemetry": rows}, message="Telemetry snapshots")

    def post(self, request):
        from apps.organisations.models import Organisation

        org_id = request.data.get("organisation_id") or get_active_organisation_id(request)
        organisation = Organisation.objects.filter(pk=org_id).first() if org_id else None
        if organisation and not user_can_access_organisation(request.user, organisation.id):
            if not is_regulator_user(request.user):
                return api_response(message="Access denied", status_code=403)
        snap = aggregate_telemetry(organisation=organisation)
        return api_response(data={"id": str(snap.id), "metrics": snap.metrics}, message="Telemetry aggregated", status_code=201)


class EscalationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = EventEscalation.objects.filter(is_acknowledged=False).order_by("-created_at")
        if not is_regulator_user(request.user) and not request.user.is_superuser:
            org_id = get_active_organisation_id(request)
            qs = qs.filter(organisation_id=org_id) if org_id else qs.none()
        rows = [
            {
                "id": str(e.id),
                "event_id": e.event_id,
                "escalation_type": e.escalation_type,
                "severity": e.severity,
                "summary": e.summary,
                "created_at": e.created_at.isoformat(),
            }
            for e in qs[:50]
        ]
        return api_response(data={"escalations": rows}, message="Live escalations")


class EventLifecycleView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        event_id = request.query_params.get("event_id")
        qs = EventLifecycleLog.objects.order_by("-created_at")
        if event_id:
            qs = qs.filter(event_id=event_id)
        rows = [
            {
                "event_id": l.event_id,
                "correlation_id": str(l.correlation_id),
                "lifecycle_state": l.lifecycle_state,
                "delivery_channel": l.delivery_channel,
                "retry_count": l.retry_count,
                "created_at": l.created_at.isoformat(),
            }
            for l in qs[:100]
        ]
        return api_response(data={"lifecycle": rows}, message="Event lifecycle audit")


class DeferredTaskQueueView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        rows = list(
            DeferredProcessingTask.objects.filter(task_status=DeferredProcessingTask.STATUS_PENDING).values(
                "id", "task_name", "task_status", "retry_count", "scheduled_at"
            )[:50]
        )
        return api_response(data={"queue": rows, "count": len(rows)}, message="Deferred task queue")


class CommandCenterLiveView(APIView):
    """Live operational snapshot for command center dashboards."""

    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        events = OperationalEventBus.replay(since_sequence=int(request.query_params.get("since_sequence", 0)), limit=30)
        escalations = EventEscalation.objects.filter(is_acknowledged=False).count()
        pending_tasks = DeferredProcessingTask.objects.filter(
            task_status=DeferredProcessingTask.STATUS_PENDING
        ).count()
        snap = aggregate_telemetry(organisation=None, window_seconds=3600)
        return api_response(
            data={
                "events": events,
                "escalations_open": escalations,
                "pending_tasks": pending_tasks,
                "telemetry": {
                    "scan_throughput": snap.scan_throughput,
                    "event_throughput": snap.event_throughput,
                    "suspicious_rate": float(snap.suspicious_rate),
                },
                "live": True,
            },
            message="Command center live feed",
        )
