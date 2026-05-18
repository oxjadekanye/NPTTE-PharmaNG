from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.certificates.models import DigitalRegulatoryCertificate
from apps.certificates.services import issue_certificate, verify_certificate
from apps.core.api.responses import api_response
from apps.core.permissions import IsRegulatorUser


class CertificateListView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        qs = DigitalRegulatoryCertificate.objects.order_by("-issued_at")[:50]
        rows = [
            {
                "certificate_number": c.certificate_number,
                "certificate_type": c.certificate_type,
                "subject_label": c.subject_label,
                "qr_verification_code": c.qr_verification_code,
                "issued_at": c.issued_at.isoformat(),
            }
            for c in qs
        ]
        return api_response(data={"certificates": rows}, message="Regulatory certificates")


class CertificateIssueView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def post(self, request):
        cert = issue_certificate(
            certificate_type=request.data.get("certificate_type", DigitalRegulatoryCertificate.CERT_BATCH_APPROVAL),
            subject_label=request.data["subject_label"],
            payload=request.data.get("payload"),
            actor=request.user,
        )
        return api_response(
            data={
                "certificate_number": cert.certificate_number,
                "qr_verification_code": cert.qr_verification_code,
                "digital_signature": cert.digital_signature[:32] + "…",
                "pdf_payload": {
                    "title": cert.subject_label,
                    "cert_no": cert.certificate_number,
                    "qr": cert.qr_verification_code,
                },
            },
            message="Certificate issued",
            status_code=201,
        )


class CertificateVerifyView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        code = request.data.get("qr_verification_code") or request.data.get("code")
        result = verify_certificate(qr_verification_code=code)
        return api_response(data=result, message="Certificate verification")
