from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.permissions import IsRegulatorUser
from apps.core.throttling import VerificationPublicThrottle
from apps.verification.api.serializers import (
    VerificationEventSerializer,
    VerificationScanLogSerializer,
    VerifySerialSerializer,
)
from apps.verification.models import VerificationEvent, VerificationScanLog
from apps.verification.services import sovereign_verify


class VerifyMedicationView(APIView):
    """Sovereign national medicine verification — serial, QR token, optional GPS."""

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [VerificationPublicThrottle]

    def post(self, request):
        ser = VerifySerialSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        result = sovereign_verify(
            request=request,
            serial_number=d.get("serial_number") or d.get("barcode", ""),
            qr_token=d.get("qr_token", ""),
            latitude=d.get("latitude"),
            longitude=d.get("longitude"),
        )
        return api_response(
            data=result["data"],
            message=result["message"],
            status_code=result["status_code"],
        )


class VerificationHistoryView(generics.ListAPIView):
    serializer_class = VerificationEventSerializer
    queryset = VerificationEvent.objects.select_related("product_serial").order_by("-created_at")[:100]

    def get_permissions(self):
        return [IsRegulatorUser()]


class VerificationScanLogListView(generics.ListAPIView):
    serializer_class = VerificationScanLogSerializer
    permission_classes = [IsRegulatorUser]
    queryset = VerificationScanLog.objects.select_related("product_serial").order_by("-created_at")
