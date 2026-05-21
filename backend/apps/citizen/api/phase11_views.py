"""Phase 11 — citizen public experience APIs."""
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.citizen.experience import (
    medication_search,
    medicine_safety_guidance,
    public_safety_notices,
    verification_history,
)
from apps.core.api.responses import api_response
from apps.core.throttling import CitizenPublicThrottle


class CitizenVerificationHistoryView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [CitizenPublicThrottle]

    def get(self, request):
        device_id = request.GET.get("device_id", "")
        return api_response(
            data={"history": verification_history(device_id=device_id or None)},
            message="Verification history",
        )


class CitizenMedicationSearchView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [CitizenPublicThrottle]

    def get(self, request):
        q = request.GET.get("q", "").strip()
        if len(q) < 2:
            return api_response(message="Query must be at least 2 characters", status_code=400)
        return api_response(
            data=medication_search(query=q, state=request.GET.get("state", "")),
            message="Medication search",
        )


class CitizenSafetyGuidanceView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [CitizenPublicThrottle]

    def get(self, request):
        return api_response(
            data=medicine_safety_guidance(
                product_name=request.GET.get("product", ""),
                outcome=request.GET.get("outcome", ""),
            ),
            message="Medicine safety guidance",
        )


class CitizenPublicNoticesView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        return api_response(data={"notices": public_safety_notices()}, message="Public safety notices")
