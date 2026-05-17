from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.permissions import IsRegulatorUser
from apps.market_intelligence.models import MarketShortageSignal, PriceManipulationAlert


class MarketPressureView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        signals = MarketShortageSignal.objects.select_related("product").order_by("-pressure_score")[:50]
        alerts = PriceManipulationAlert.objects.filter(is_confirmed=False).select_related("product")[:30]
        return api_response(
            data={
                "shortage_signals": [
                    {"product": s.product.name, "state": s.state, "pressure": str(s.pressure_score)}
                    for s in signals
                ],
                "price_alerts": [
                    {"product": a.product.name, "spike_percent": str(a.spike_percent)} for a in alerts
                ],
            }
        )
