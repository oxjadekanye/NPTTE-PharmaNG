from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.constants import RegulatorBatchStatus
from apps.core.permissions import IsRegulatorUser
from apps.products.models import ProductBatch
from apps.products.services import approve_batch, suspend_batch
from apps.regulatory.api.serializers import (
    BatchApprovalSerializer,
    BatchSuspendSerializer,
    PendingBatchSerializer,
)


class PendingBatchesView(generics.ListAPIView):
    """Batches awaiting regulator approval."""

    serializer_class = PendingBatchSerializer
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get_queryset(self):
        return ProductBatch.objects.filter(
            regulator_status=RegulatorBatchStatus.PENDING,
            is_active=True,
        ).select_related(
            "product",
            "manufacturing_site",
            "manufacturing_site__manufacturer",
            "manufacturing_site__manufacturer__organisation",
        )


class BatchApproveView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def post(self, request, pk):
        ser = BatchApprovalSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        batch = get_object_or_404(ProductBatch, pk=pk)
        approve_batch(batch=batch, actor=request.user, request=request, notes=ser.validated_data.get("notes", ""))
        return api_response(
            data=PendingBatchSerializer(batch).data,
            message="Batch approved for national circulation",
            status_code=status.HTTP_200_OK,
        )


class BatchSuspendView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def post(self, request, pk):
        ser = BatchSuspendSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        batch = get_object_or_404(ProductBatch, pk=pk)
        suspend_batch(batch=batch, actor=request.user, request=request, reason=ser.validated_data["reason"])
        return api_response(
            data=PendingBatchSerializer(batch).data,
            message="Batch suspended",
            status_code=status.HTTP_200_OK,
        )
