from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.analytics.services import (
    national_inventory_summary,
    state_inventory_breakdown,
    top_products_by_stock,
    transaction_volume_by_type,
)
from apps.core.api.responses import api_response
from apps.core.permissions import IsRegulatorUser


class NationalInventorySummaryView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        return api_response(data=national_inventory_summary())


class TransactionVolumeView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        return api_response(data={"volumes": transaction_volume_by_type()})


class StateBreakdownView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        return api_response(data={"states": state_inventory_breakdown()})


class TopProductsView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        limit = int(request.query_params.get("limit", 10))
        return api_response(data={"products": top_products_by_stock(limit=limit)})
