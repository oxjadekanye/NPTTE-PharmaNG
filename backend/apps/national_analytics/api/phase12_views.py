"""Phase 12 — extended national analytics APIs."""
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.permissions import IsRegulatorUser
from apps.national_analytics.operations_engine import (
    enforcement_productivity,
    export_dashboard_bundle,
    national_scan_analytics,
    regional_intelligence_trends,
)


class NationalScanAnalyticsView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        return api_response(data=national_scan_analytics(), message="National scan analytics")


class RegionalTrendsView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        return api_response(
            data={"trends": regional_intelligence_trends()},
            message="Regional intelligence trends",
        )


class AnalyticsExportBundleView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        bundle = export_dashboard_bundle()
        bundle["enforcement_productivity"] = enforcement_productivity()
        return api_response(data=bundle, message="Export-ready analytics bundle")
