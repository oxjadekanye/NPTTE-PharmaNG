from django_filters import rest_framework as filters
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.permissions import IsRegulatorUser
from apps.core.roles import is_regulator_user
from apps.organisations.models import Organisation
from apps.products.models import Product, ProductBatch
from apps.serialization.models import ProductSerial
from apps.traceability.api.permissions import CanRecordTransaction, CanViewNationalTraceability
from apps.traceability.api.serializers import (
    BatchRecallSerializer,
    SupplyChainTransactionCreateSerializer,
    SupplyChainTransactionSerializer,
)
from apps.traceability.models import BatchRecall, SupplyChainTransaction
from apps.traceability.services import record_supply_chain_transaction


class SupplyChainTransactionFilter(filters.FilterSet):
    transaction_type = filters.CharFilter()
    source_organisation = filters.UUIDFilter()
    destination_organisation = filters.UUIDFilter()
    product = filters.UUIDFilter()
    verification_status = filters.CharFilter()
    risk_level = filters.CharFilter()
    created_at_after = filters.IsoDateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_at_before = filters.IsoDateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = SupplyChainTransaction
        fields = ["transaction_type", "verification_status", "risk_level"]


class SupplyChainTransactionListView(generics.ListAPIView):
    serializer_class = SupplyChainTransactionSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = SupplyChainTransactionFilter
    queryset = SupplyChainTransaction.objects.select_related(
        "actor",
        "source_organisation",
        "destination_organisation",
        "product",
        "batch",
    ).order_by("-created_at")

    def get_permissions(self):
        if self.request.method == "GET" and is_regulator_user(self.request.user):
            return [IsAuthenticated(), CanViewNationalTraceability()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if is_regulator_user(user) or user.is_superuser:
            return qs
        if user.organisation_id:
            from django.db.models import Q

            return qs.filter(
                Q(source_organisation_id=user.organisation_id)
                | Q(destination_organisation_id=user.organisation_id)
            ).distinct()
        return qs.none()


class SupplyChainTransactionCreateView(APIView):
    permission_classes = [IsAuthenticated, CanRecordTransaction]

    def post(self, request):
        ser = SupplyChainTransactionCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data

        txn = record_supply_chain_transaction(
            transaction_type=d["transaction_type"],
            request=request,
            actor=request.user,
            source_organisation=Organisation.objects.filter(
                id=d.get("source_organisation_id")
            ).first(),
            destination_organisation=Organisation.objects.filter(
                id=d.get("destination_organisation_id")
            ).first(),
            product=Product.objects.filter(id=d.get("product_id")).first(),
            batch=ProductBatch.objects.filter(id=d.get("batch_id")).first(),
            product_serial=ProductSerial.objects.filter(id=d.get("product_serial_id")).first(),
            quantity_delta=d.get("quantity_delta", 0),
            latitude=d.get("latitude"),
            longitude=d.get("longitude"),
            notes=d.get("notes", ""),
        )
        return api_response(
            data=SupplyChainTransactionSerializer(txn).data,
            message="Transaction recorded",
            status_code=status.HTTP_201_CREATED,
        )


class SupplyChainTransactionDetailView(generics.RetrieveAPIView):
    serializer_class = SupplyChainTransactionSerializer
    permission_classes = [IsAuthenticated]
    queryset = SupplyChainTransaction.objects.all()
    lookup_field = "audit_reference"


class BatchRecallListView(generics.ListAPIView):
    serializer_class = BatchRecallSerializer
    permission_classes = [IsAuthenticated, IsRegulatorUser]
    queryset = BatchRecall.objects.select_related("batch").order_by("-effective_at")
