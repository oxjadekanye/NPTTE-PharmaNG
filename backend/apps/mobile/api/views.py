import uuid

from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.mobile.models import DeviceRegistration
from apps.mobile.scanner import ingest_scan, sync_offline_queue
from apps.mobile.serializers import MobileDeviceSerializer


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
