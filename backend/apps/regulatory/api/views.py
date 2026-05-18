from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.constants import RegulatorBatchStatus
from apps.core.permissions import IsRegulatorUser
from apps.organisations.models import Organisation
from apps.products.models import ProductBatch
from apps.products.services import approve_batch, issue_national_batch_recall, reject_batch, suspend_batch
from apps.regulatory.api.serializers import (
    BatchApprovalSerializer,
    BatchRejectSerializer,
    BatchSuspendSerializer,
    NationalBatchRecallSerializer,
    PendingBatchSerializer,
)
from apps.serialization.models import ProductSerial
from apps.traceability.api.serializers import BatchRegulatoryAuditSerializer
from apps.traceability.models import BatchRegulatoryAudit
from apps.traceability.services import list_pharmacy_organisations_holding_batch
from apps.verification.services import sovereign_verify


class BatchRecallAffectedView(APIView):
    """List pharmacy organisations with on-hand stock for a batch (recall enforcement)."""

    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        bid = request.query_params.get("batch_id")
        if not bid:
            return api_response(message="batch_id query parameter required", status_code=400)
        batch = get_object_or_404(ProductBatch, pk=bid)
        affected = list_pharmacy_organisations_holding_batch(batch=batch)
        return api_response(data={"pharmacy_organisation_ids": [str(x) for x in affected]})


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


class BatchRejectView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def post(self, request, pk):
        ser = BatchRejectSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        batch = get_object_or_404(ProductBatch, pk=pk)
        reject_batch(batch=batch, actor=request.user, request=request, reason=ser.validated_data["reason"])
        return api_response(data=PendingBatchSerializer(batch).data, message="Batch rejected")


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


class BatchRecallView(APIView):
    """Issue national recall for a batch (Phase 8 enforcement)."""

    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def post(self, request, pk):
        ser = NationalBatchRecallSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        batch = get_object_or_404(ProductBatch, pk=pk)
        org = None
        oid = ser.validated_data.get("issued_by_organisation_id")
        if oid:
            org = Organisation.objects.filter(pk=oid).first()
        recall = issue_national_batch_recall(
            batch=batch,
            actor=request.user,
            request=request,
            reason=ser.validated_data["reason"],
            issued_by_organisation=org,
        )
        affected = list_pharmacy_organisations_holding_batch(batch=batch)
        return api_response(
            data={
                "recall_id": str(recall.id),
                "batch": PendingBatchSerializer(batch).data,
                "pharmacy_organisation_ids_affected": [str(x) for x in affected],
            },
            message="National recall issued",
            status_code=status.HTTP_201_CREATED,
        )


class BatchAuditTrailView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]
    serializer_class = BatchRegulatoryAuditSerializer

    def get_queryset(self):
        batch = get_object_or_404(ProductBatch, pk=self.kwargs["pk"])
        return BatchRegulatoryAudit.objects.filter(batch=batch).order_by("-created_at")


class RegulatorSerialLookupView(APIView):
    """Read-only serial lookup for regulators (no public scan side-effects)."""

    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def post(self, request):
        sn = (request.data.get("serial_number") or "").strip()
        if not sn:
            return api_response(message="serial_number required", status_code=400)
        try:
            serial = ProductSerial.objects.select_related(
                "batch", "batch__product", "batch__product__manufacturer", "custody_organisation"
            ).get(serial_number=sn)
        except ProductSerial.DoesNotExist:
            return api_response(message="Serial not found", status_code=404)
        b = serial.batch
        data = {
            "serial_number": serial.serial_number,
            "is_dispensed": serial.is_dispensed,
            "scan_count": serial.scan_count,
            "custody_organisation_id": str(serial.custody_organisation_id) if serial.custody_organisation_id else None,
            "batch": {
                "id": str(b.id),
                "batch_number": b.batch_number,
                "regulator_status": b.regulator_status,
                "lifecycle_status": b.lifecycle_status,
                "expiry_date": b.expiry_date,
            },
            "product": {"name": b.product.name, "brand_name": b.product.brand_name},
        }
        return api_response(data=data, message="Lookup complete")


class RegulatorSovereignVerifyView(APIView):
    """Authenticated regulator path to run verification engine (same payload as public)."""

    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def post(self, request):
        from apps.verification.api.serializers import VerifySerialSerializer

        ser = VerifySerialSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        result = sovereign_verify(
            request=request,
            serial_number=d.get("serial_number") or d.get("barcode", ""),
            qr_token=d.get("qr_token", ""),
            latitude=d.get("latitude"),
            longitude=d.get("longitude"),
            device_id=d.get("device_id"),
        )
        return api_response(
            data=result["data"],
            message=result["message"],
            status_code=result["status_code"],
        )
