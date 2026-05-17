from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.permissions import IsRegulatorUser
from apps.national_analytics.services import NationalAnalyticsService


class _AnalyticsView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]
    service_method = ""

    def get(self, request):
        data = getattr(NationalAnalyticsService, self.service_method)()
        return api_response(data=data)


class NationalSummaryView(_AnalyticsView):
    service_method = "national_summary"


class HeatmapsView(_AnalyticsView):
    service_method = "heatmaps"


class MedicineFlowView(_AnalyticsView):
    service_method = "medicine_flow"


class RiskAnalysisView(_AnalyticsView):
    service_method = "risk_analysis"


class StateComparisonView(_AnalyticsView):
    service_method = "state_comparison"
