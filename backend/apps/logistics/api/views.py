from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.constants import ShipmentLifecycle
from apps.core.permissions import IsLogisticsStaff
from apps.core.roles import is_regulator_user
from apps.logistics.api.serializers import (
    CheckpointSerializer,
    DeliveryConfirmSerializer,
    LogisticsShipmentSerializer,
    ShipmentCreateSerializer,
)
from apps.logistics.models import (
    DeliveryConfirmation,
    LogisticsProviderProfile,
    LogisticsShipment,
    ShipmentItem,
)
from apps.logistics.services import record_shipment_checkpoint
from apps.products.models import ProductBatch


class ShipmentListCreateView(generics.ListCreateAPIView):
    serializer_class = LogisticsShipmentSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsLogisticsStaff()]

    def get_queryset(self):
        user = self.request.user
        qs = LogisticsShipment.objects.select_related(
            "origin_organisation",
            "destination_organisation",
            "logistics_provider",
        ).prefetch_related("items")
        if is_regulator_user(user):
            return qs.order_by("-created_at")[:200]
        if user.organisation_id:
            from django.db.models import Q

            return qs.filter(
                Q(origin_organisation_id=user.organisation_id)
                | Q(destination_organisation_id=user.organisation_id)
            ).distinct()
        return qs.none()

    def create(self, request, *args, **kwargs):
        ser = ShipmentCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        provider = LogisticsProviderProfile.objects.get(
            organisation_id=request.user.organisation_id
        )
        shipment = LogisticsShipment.objects.create(
            tracking_number=d["tracking_number"],
            logistics_provider=provider,
            origin_organisation_id=d["origin_organisation_id"],
            destination_organisation_id=d["destination_organisation_id"],
            temperature_controlled=d.get("temperature_controlled", False),
            lifecycle_status=ShipmentLifecycle.CREATED,
            created_by=request.user,
        )
        for batch_id in d.get("batch_ids", []):
            batch = ProductBatch.objects.get(id=batch_id)
            ShipmentItem.objects.create(
                shipment=shipment,
                batch=batch,
                quantity=1,
                created_by=request.user,
            )
        return api_response(
            data=LogisticsShipmentSerializer(shipment).data,
            message="Shipment created",
            status_code=status.HTTP_201_CREATED,
        )


class ShipmentDetailView(generics.RetrieveAPIView):
    serializer_class = LogisticsShipmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return LogisticsShipment.objects.prefetch_related("items")


class ShipmentCheckpointView(APIView):
    permission_classes = [IsAuthenticated, IsLogisticsStaff]

    def post(self, request, pk):
        shipment = LogisticsShipment.objects.get(pk=pk)
        ser = CheckpointSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        checkpoint = record_shipment_checkpoint(
            shipment=shipment,
            latitude=d["latitude"],
            longitude=d["longitude"],
            temperature_celsius=d.get("temperature_celsius"),
            condition_notes=d.get("condition_notes", ""),
            request=request,
            actor=request.user,
        )
        return api_response(
            data={"checkpoint_id": str(checkpoint.id), "lifecycle": shipment.lifecycle_status},
            message="Checkpoint recorded",
        )


class ShipmentDeliveryConfirmView(APIView):
    permission_classes = [IsAuthenticated, IsLogisticsStaff]

    def post(self, request, pk):
        shipment = LogisticsShipment.objects.get(pk=pk)
        ser = DeliveryConfirmSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        DeliveryConfirmation.objects.create(
            shipment=shipment,
            received_by_name=d["received_by_name"],
            quantity_received=d["quantity_received"],
            rejection_reason=d.get("rejection_reason", ""),
            confirmed_at=timezone.now(),
            created_by=request.user,
        )
        shipment.lifecycle_status = (
            ShipmentLifecycle.VERIFIED if not d.get("rejection_reason") else ShipmentLifecycle.REJECTED
        )
        shipment.delivered_at = timezone.now()
        shipment.save(update_fields=["lifecycle_status", "delivered_at", "updated_at"])
        return api_response(data=LogisticsShipmentSerializer(shipment).data, message="Delivery confirmed")
