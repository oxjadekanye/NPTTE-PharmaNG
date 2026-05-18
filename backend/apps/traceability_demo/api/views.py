from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.traceability_demo.story import build_traceability_story


class TraceabilityStoryView(APIView):
    """Phase 13 — public demo walkthrough payload (no production data)."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        return api_response(data=build_traceability_story(), message="Traceability demo story")
