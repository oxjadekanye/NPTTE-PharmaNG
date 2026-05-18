import json

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.organisations.models import Organisation
from apps.scanning.models import ScanEvent
from apps.scanning.services import ingest_scan_event, serialize_scan_event


def _scan_type_from_request(request) -> str:
    if hasattr(request, "data") and request.data:
        return request.data.get("scan_type", ScanEvent.SCAN_CITIZEN)
    try:
        body = json.loads(request.body.decode() or "{}")
        return body.get("scan_type", ScanEvent.SCAN_CITIZEN)
    except (json.JSONDecodeError, AttributeError, UnicodeDecodeError):
        return ScanEvent.SCAN_CITIZEN


class ScanIngestView(APIView):
    """Phase 12 — unified mobile scan ingestion."""

    def get_authenticators(self):
        if _scan_type_from_request(self.request) == ScanEvent.SCAN_CITIZEN:
            return []
        return super().get_authenticators()

    def get_permissions(self):
        if _scan_type_from_request(self.request) == ScanEvent.SCAN_CITIZEN:
            return [AllowAny()]
        return [IsAuthenticated()]

    def post(self, request):
        data = request.data
        serial = data.get("serial_number", "")
        scan_type = data.get("scan_type", ScanEvent.SCAN_CITIZEN)
        org = None
        org_id = data.get("organisation") or data.get("organisation_id")
        if org_id:
            org = Organisation.objects.filter(pk=org_id).first()
        elif getattr(request.user, "organisation_id", None):
            org = Organisation.objects.filter(pk=request.user.organisation_id).first()

        sync_status = data.get("sync_status", ScanEvent.SYNC_SYNCED)
        event = ingest_scan_event(
            request=request,
            serial_number=serial,
            scan_type=scan_type,
            actor_role=data.get("actor_role", ""),
            organisation=org,
            device_id=data.get("device_id", ""),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            offline_timestamp=data.get("offline_timestamp"),
            sync_status=sync_status,
            replay_nonce=data.get("replay_nonce", ""),
            user=request.user if request.user.is_authenticated else None,
        )
        return api_response(data=serialize_scan_event(event), message="Scan ingested", status_code=201)


class ScanHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serial = request.query_params.get("serial_number")
        qs = ScanEvent.objects.order_by("-created_at")
        if serial:
            qs = qs.filter(serial_number=serial)
        if not request.user.is_staff:
            role = getattr(request.user, "role_code", "") or ""
            if "NAFDAC" not in role and "REGULATOR" not in role:
                qs = qs.filter(user=request.user)
        rows = [serialize_scan_event(e) for e in qs[:50]]
        return api_response(data={"scans": rows, "count": len(rows)}, message="Scan history")


class ScanSyncPendingView(APIView):
    """Process client-queued offline scans (batch)."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        items = request.data.get("items") or []
        results = []
        for item in items:
            event = ingest_scan_event(
                request=request,
                serial_number=item.get("serial_number", ""),
                scan_type=item.get("scan_type", ScanEvent.SCAN_CITIZEN),
                actor_role=item.get("actor_role", ""),
                device_id=item.get("device_id", ""),
                latitude=item.get("latitude"),
                longitude=item.get("longitude"),
                offline_timestamp=item.get("offline_timestamp"),
                sync_status=ScanEvent.SYNC_SYNCED,
                replay_nonce=item.get("replay_nonce", ""),
                user=request.user,
            )
            results.append(serialize_scan_event(event))
        return api_response(
            data={"synced": len(results), "results": results},
            message="Offline batch synced",
        )
