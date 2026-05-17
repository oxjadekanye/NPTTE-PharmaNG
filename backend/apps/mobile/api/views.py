import uuid

from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.mobile.models import DeviceRegistration
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


class DeviceListView(generics.ListAPIView):
    serializer_class = MobileDeviceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.organisation_id:
            return DeviceRegistration.objects.filter(organisation_id=user.organisation_id)[:50]
        return DeviceRegistration.objects.none()
