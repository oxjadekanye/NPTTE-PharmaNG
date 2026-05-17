from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.constants import VerificationChannel, VerificationStatus
from apps.core.throttling import VerificationPublicThrottle
from apps.fraud_detection.services import create_fraud_flag, score_inventory_anomaly
from apps.serialization.models import ProductSerial
from apps.serialization.services import ensure_qr_payload
from apps.traceability.services import check_batch_recall
from apps.verification.api.serializers import VerificationEventSerializer, VerifySerialSerializer
from apps.verification.models import VerificationEvent


class VerifyMedicationView(APIView):
    """Public medication authenticity verification by serial or barcode."""

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [VerificationPublicThrottle]

    def post(self, request):
        ser = VerifySerialSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        serial_number = ser.validated_data["serial_number"] or ser.validated_data.get("barcode")
        try:
            product_serial = ProductSerial.objects.select_related("batch", "batch__product").get(
                serial_number=serial_number
            )
        except ProductSerial.DoesNotExist:
            return api_response(
                data={"is_authentic": False, "verification_status": VerificationStatus.FAILED},
                message="Serial number not found in national registry.",
                status_code=404,
            )

        recall = check_batch_recall(product_serial.batch)
        is_authentic = not recall and not product_serial.is_dispensed
        status_label = VerificationStatus.VERIFIED if is_authentic else VerificationStatus.SUSPICIOUS
        message = "Authentic medicine pack registered with NPTTE."
        if recall:
            status_label = VerificationStatus.RECALLED
            message = "This batch is under national recall."
            is_authentic = False
        elif product_serial.is_dispensed:
            status_label = VerificationStatus.SUSPICIOUS
            message = "Serial already marked dispensed — verify with pharmacy."
            is_authentic = False

        ensure_qr_payload(product_serial)
        event = VerificationEvent.objects.create(
            product_serial=product_serial,
            channel=VerificationChannel.QR,
            is_authentic=is_authentic,
            verification_message=message,
            client_ip=request.META.get("REMOTE_ADDR"),
            user_agent=(request.META.get("HTTP_USER_AGENT") or "")[:512],
        )

        if not is_authentic:
            risk = score_inventory_anomaly(organisation=None, quantity_delta=100)
            create_fraud_flag(
                flag_type="counterfeit_verification_failure",
                supply_chain_transaction=None,
                risk_score=risk,
                description=f"Failed verification for serial {serial_number}",
            )

        return api_response(
            data={
                "is_authentic": is_authentic,
                "verification_status": status_label,
                "serial_number": product_serial.serial_number,
                "qr_payload": product_serial.qr_payload,
                "product": {
                    "name": product_serial.batch.product.name,
                    "brand_name": product_serial.batch.product.brand_name,
                    "strength": product_serial.batch.product.strength,
                    "dosage_form": product_serial.batch.product.dosage_form,
                    "dosage_guidance": product_serial.batch.product.dosage_guidance,
                },
                "batch_number": product_serial.batch.batch_number,
                "expiry_date": product_serial.batch.expiry_date,
                "verified_at": timezone.now().isoformat(),
                "event_id": str(event.id),
            },
            message=message,
        )


class VerificationHistoryView(generics.ListAPIView):
    serializer_class = VerificationEventSerializer
    queryset = VerificationEvent.objects.select_related("product_serial").order_by("-created_at")[:100]

    def get_permissions(self):
        from apps.core.permissions import IsRegulatorUser

        return [IsRegulatorUser()]
