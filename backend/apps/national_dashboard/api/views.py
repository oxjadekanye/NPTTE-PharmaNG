from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.alerts.models import NationalAlert
from apps.analytics.services import (
    national_inventory_summary,
    state_inventory_breakdown,
    transaction_volume_by_type,
)
from apps.core.api.responses import api_response
from apps.core.permissions import IsRegulatorUser
from apps.fraud_detection.models import FraudRiskFlag
from apps.traceability.models import SupplyChainTransaction


class NationalOverviewDashboardView(APIView):
    """NAFDAC / FMOH / NDLEA national overview dashboard data."""

    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        return api_response(
            data={
                "inventory": national_inventory_summary(),
                "transaction_volumes": transaction_volume_by_type(),
                "state_breakdown": state_inventory_breakdown()[:10],
                "open_alerts": NationalAlert.objects.filter(
                    resolved_at__isnull=True, is_active=True
                ).count(),
                "unresolved_fraud_flags": FraudRiskFlag.objects.filter(
                    is_resolved=False
                ).count(),
                "high_risk_transactions": SupplyChainTransaction.objects.filter(
                    risk_level__in=["high", "critical"]
                ).count(),
            },
            message="National dashboard overview",
        )
