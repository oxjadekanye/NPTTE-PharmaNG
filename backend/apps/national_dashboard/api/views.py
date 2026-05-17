from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.permissions import IsRegulatorUser
from apps.national_dashboard.services import NationalCommandMetricsService


class _RegulatorDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]
    metric_method = None

    def get(self, request):
        data = getattr(NationalCommandMetricsService, self.metric_method)()
        return api_response(data=data)


class NationalOverviewDashboardView(_RegulatorDashboardView):
    metric_method = "national_overview"


class CounterfeitMapView(_RegulatorDashboardView):
    metric_method = "counterfeit_map"


class ShortagesDashboardView(_RegulatorDashboardView):
    metric_method = "shortages"


class SupplyChainDashboardView(_RegulatorDashboardView):
    metric_method = "supply_chain"


class HighRiskOrganisationsView(_RegulatorDashboardView):
    metric_method = "high_risk_organisations"


class VerificationTrafficView(_RegulatorDashboardView):
    metric_method = "verification_traffic"


class StateAnalyticsView(_RegulatorDashboardView):
    metric_method = "state_analytics"
