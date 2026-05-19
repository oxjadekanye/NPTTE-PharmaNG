import uuid

from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.roles import is_regulator_user
from apps.mobile.models import DeviceRegistration, MobileFieldEvidence, MobileOperationalAudit
from apps.mobile.scanner import ingest_scan, sync_offline_queue
from apps.mobile.serializers import MobileDeviceSerializer
from apps.mobile.services.device_trust import device_heartbeat, register_device_trust
from apps.mobile.services.evidence import create_field_evidence, sync_pending_evidence
from apps.mobile.services.mobile_audit import record_mobile_audit
from apps.copilot.services.reasoning import run_copilot_reasoning


class DeviceRegisterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        device_id = request.data.get("device_id") or uuid.uuid4().hex
        device, _ = DeviceRegistration.objects.update_or_create(
            device_id=device_id,
            defaults={
                "device_type": request.data.get("device_type", "android"),
                "organisation_id": request.user.organisation_id,
                "app_version": request.data.get("app_version", ""),
                "offline_sync_token": uuid.uuid4().hex[:32],
                "last_sync_at": timezone.now(),
                "created_by": request.user,
            },
        )
        return api_response(
            data={
                **MobileDeviceSerializer(device).data,
                "offline_sync_token": device.offline_sync_token,
            },
            message="Device registered",
        )


class ScanIngestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        result = ingest_scan(
            request=request,
            raw_scan=request.data.get("raw_scan", ""),
            scan_source=request.data.get("scan_source", "mobile"),
            scanner_type=request.data.get("scanner_type", "mobile_camera"),
            device_id=request.data.get("device_id"),
            latitude=request.data.get("latitude"),
            longitude=request.data.get("longitude"),
            replay_nonce=request.data.get("replay_nonce", ""),
            offline=request.data.get("offline", False),
        )
        if result.get("queued"):
            return api_response(data=result, message="Scan queued for offline sync", status_code=202)
        return api_response(data=result["data"], message=result["message"], status_code=result["status_code"])


class OfflineSyncView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        device = DeviceRegistration.objects.get(device_id=request.data["device_id"])
        stats = sync_offline_queue(device=device, request=request)
        return api_response(data=stats, message="Offline sync completed")


class DeviceListView(generics.ListAPIView):
    serializer_class = MobileDeviceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.organisation_id:
            return DeviceRegistration.objects.filter(organisation_id=user.organisation_id)[:50]
        return DeviceRegistration.objects.none()


class DeviceTrustView(APIView):
    """Phase 22 — trusted device registration with risk metadata."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        device_id = request.data.get("device_id") or uuid.uuid4().hex
        device = register_device_trust(
            request=request,
            device_id=device_id,
            fingerprint=request.data.get("fingerprint", device_id),
            platform=request.data.get("platform", "unknown"),
            app_version=request.data.get("app_version", ""),
            os_version=request.data.get("os_version", ""),
            is_emulator=bool(request.data.get("is_emulator")),
            is_rooted=bool(request.data.get("is_rooted")),
            suspicious=bool(request.data.get("suspicious")),
            biometric_capable=bool(request.data.get("biometric_capable")),
        )
        return api_response(
            data={
                "device_id": device.device_id,
                "trusted_status": device.trusted_status,
                "device_risk_level": device.device_risk_level,
                "trust_score": float(device.trust_score),
                "offline_sync_token": device.offline_sync_token,
                "suspicious_device": device.suspicious_device,
            },
            message="Device trust registered",
        )


class DeviceHeartbeatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        result = device_heartbeat(
            request=request,
            device_id=request.data["device_id"],
            app_version=request.data.get("app_version", ""),
            rotate_session=bool(request.data.get("rotate_session")),
        )
        status = 200 if result.get("ok") else 404
        return api_response(data=result, message="Heartbeat", status_code=status)


class FieldEvidenceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ev = create_field_evidence(
            request=request,
            device_id=request.data["device_id"],
            evidence_type=request.data.get("evidence_type", "field_photo"),
            notes=request.data.get("notes", ""),
            serial_number=request.data.get("serial_number", ""),
            case_id=request.data.get("case_id"),
            latitude=request.data.get("latitude"),
            longitude=request.data.get("longitude"),
            photos=request.data.get("photos") or [],
        )
        return api_response(
            data={"id": str(ev.id), "sync_status": ev.sync_status},
            message="Evidence captured",
            status_code=201,
        )

    def get(self, request):
        qs = MobileFieldEvidence.objects.filter(actor=request.user).order_by("-created_at")[:50]
        rows = [
            {
                "id": str(e.id),
                "evidence_type": e.evidence_type,
                "serial_number": e.serial_number,
                "sync_status": e.sync_status,
                "created_at": e.created_at.isoformat(),
            }
            for e in qs
        ]
        return api_response(data={"evidence": rows}, message="Evidence list")


class EvidenceSyncView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        stats = sync_pending_evidence(request=request, device_id=request.data["device_id"])
        return api_response(data=stats, message="Evidence sync")


class MobileAuditTimelineView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = MobileOperationalAudit.objects.filter(actor=request.user).select_related("device")[:80]
        rows = [
            {
                "id": str(a.id),
                "action_type": a.action_type,
                "payload": a.payload,
                "sync_status": a.sync_status,
                "device_id": a.device.device_id if a.device_id else None,
                "created_at": a.created_at.isoformat(),
            }
            for a in qs
        ]
        return api_response(data={"timeline": rows}, message="Mobile audit timeline")


class MobileRealtimeFeedView(APIView):
    """Lightweight mobile realtime — scoped streambus replay."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.streambus.services.bus import OperationalEventBus

        channel = request.query_params.get("channel", "officer_tasks")
        since = int(request.query_params.get("since_sequence", 0))
        events = OperationalEventBus.replay(since_sequence=since, limit=30)
        filtered = []
        for ev in events:
            payload = ev.get("payload") if isinstance(ev.get("payload"), dict) else {}
            ch = payload.get("stream_channel", "national")
            if channel in ("all", ch):
                filtered.append(ev)
        return api_response(
            data={"channel": channel, "events": filtered[:20], "patches": []},
            message="Mobile realtime feed",
        )


class MobileCopilotView(APIView):
    """Phase 22 — mobile field AI (manual trigger, copilot backend)."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not (is_regulator_user(request.user) or request.user.is_superuser):
            return api_response(message="regulator_only", status_code=403)
        mode = request.data.get("prompt_mode", "explain_risk")
        payload, reason = run_copilot_reasoning(
            request=request,
            mode=mode,
            entity_type=request.data.get("entity_type"),
            entity_id=request.data.get("entity_id"),
            context_key=request.data.get("context_key"),
            user_question=request.data.get("user_question"),
        )
        if payload is None:
            return api_response(message=reason or "denied", status_code=403)
        record_mobile_audit(
            request=request,
            action_type="mobile.ai.request",
            payload={"mode": mode},
        )
        return api_response(data=payload, message="Mobile AI response")
