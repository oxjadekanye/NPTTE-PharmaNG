from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.citizen.api.serializers import CounterfeitReportSerializer, PublicVerifySerializer
from apps.citizen.models import CitizenFraudReport, PublicRecallNotice
from apps.citizen.services import get_or_create_session, pharmacy_trust_score, record_citizen_verification
from apps.core.api.responses import api_response
from apps.core.constants import EventCategory
from apps.core.security import log_security_threat, request_fingerprint
from apps.core.throttling import CitizenPublicThrottle
from apps.events.services import EventStreamService
from apps.pharmacies.models import PharmacyProfile
from apps.verification.services import sovereign_verify


class PublicVerifyView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [CitizenPublicThrottle]

    def post(self, request):
        ser = PublicVerifySerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        if not any([d.get("serial_number"), d.get("qr_token"), d.get("barcode")]):
            log_security_threat(request, "citizen_empty_verify", severity="low")
            return api_response(message="Serial or QR token required", status_code=400)
        session = get_or_create_session(request=request)
        if session.verification_count > 50:
            log_security_threat(request, "citizen_abuse_throttle", severity="high", fingerprint=request_fingerprint(request))
            return api_response(message="Rate limit exceeded", status_code=429)
        result = sovereign_verify(
            request=request,
            serial_number=d.get("serial_number") or d.get("barcode", ""),
            qr_token=d.get("qr_token", ""),
            latitude=d.get("latitude"),
            longitude=d.get("longitude"),
            device_id=d.get("device_id") or None,
        )
        record_citizen_verification(
            session=session,
            serial_number=d.get("serial_number") or d.get("barcode", ""),
            outcome=result["data"].get("outcome", "unknown"),
        )
        EventStreamService.publish_event(
            category=EventCategory.VERIFICATION,
            event_type="citizen_public_verify",
            payload=result["data"],
            extra_fields={"serial_number": d.get("serial_number", "")},
        )
        return api_response(data=result["data"], message=result["message"], status_code=result["status_code"])


class ReportCounterfeitView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [CitizenPublicThrottle]

    def post(self, request):
        ser = CounterfeitReportSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        session = get_or_create_session(request=request)
        report = CitizenFraudReport.objects.create(
            session=session,
            serial_number=d.get("serial_number", ""),
            pharmacy_name=d.get("pharmacy_name", ""),
            description=d["description"],
            state=d.get("state", ""),
            latitude=d.get("latitude"),
            longitude=d.get("longitude"),
        )
        EventStreamService.publish_event(
            category=EventCategory.FRAUD,
            event_type="citizen_counterfeit_report",
            payload={"report_id": str(report.id)},
        )
        return api_response(data={"report_id": str(report.id)}, message="Report submitted for regulator review")


class PublicRecallsView(generics.ListAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [CitizenPublicThrottle]
    queryset = PublicRecallNotice.objects.filter(is_active=True).select_related("product").order_by("-published_at")[:50]

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        data = [
            {
                "recall_number": r.recall_number,
                "title": r.title,
                "product": r.product.name,
                "published_at": r.published_at.isoformat(),
            }
            for r in qs
        ]
        return api_response(data={"recalls": data})


class TrustedPharmaciesView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [CitizenPublicThrottle]

    def get(self, request):
        state = request.query_params.get("state", "")
        qs = PharmacyProfile.objects.filter(is_active=True).select_related("organisation")
        if state:
            qs = qs.filter(organisation__state=state)
        data = [
            {
                "name": p.organisation.trading_name or p.organisation.legal_name,
                "state": p.organisation.state,
                "city": p.organisation.city,
                "trust_score": str(pharmacy_trust_score(p)),
                "verified": p.is_national_registry_verified,
            }
            for p in qs[:100]
        ]
        return api_response(data={"pharmacies": data})
