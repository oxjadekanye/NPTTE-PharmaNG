"""Pharmacy API views."""
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.api.mixins import AuditLogViewMixin
from apps.core.constants import AvailabilityStatus
from apps.core.permissions import (
    IsPharmacyInventoryManager,
    IsPharmacyStaff,
    IsPharmacyStaffOrRegulator,
    IsRegulatorUser,
)
from apps.core.roles import is_regulator_user
from apps.inventory.models import InventoryItem
from apps.pharmacies.api.serializers import (
    InventoryItemSerializer,
    InventoryUpdateSerializer,
    PharmacyProfileSerializer,
    PharmacyProfileUpdateSerializer,
)
from apps.pharmacies.models import PharmacyProfile


class PharmacyProfileView(AuditLogViewMixin, generics.RetrieveUpdateAPIView):
    """Pharmacy profile for the authenticated user's organisation."""

    audit_entity_type = "pharmacy_profile"
    def get_permissions(self):
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            return [IsAuthenticated(), IsPharmacyStaffOrRegulator()]
        return [IsAuthenticated(), IsPharmacyStaff()]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return PharmacyProfileUpdateSerializer
        return PharmacyProfileSerializer

    def get_object(self):
        user = self.request.user
        if is_regulator_user(user) and self.request.query_params.get("organisation_id"):
            return PharmacyProfile.objects.select_related("organisation").get(
                organisation_id=self.request.query_params["organisation_id"]
            )
        if not user.organisation_id:
            from rest_framework.exceptions import NotFound

            raise NotFound("No organisation linked to this user.")
        return PharmacyProfile.objects.select_related("organisation").get(
            organisation_id=user.organisation_id
        )


class PharmacyInventoryListCreateView(AuditLogViewMixin, generics.ListCreateAPIView):
    audit_entity_type = "inventory_item"
    serializer_class = InventoryItemSerializer
    permission_classes = [IsAuthenticated, IsPharmacyInventoryManager]

    def get_queryset(self):
        user = self.request.user
        qs = InventoryItem.objects.filter(is_active=True).select_related("product", "organisation")
        if is_regulator_user(user) and self.request.query_params.get("organisation_id"):
            return qs.filter(organisation_id=self.request.query_params["organisation_id"])
        return qs.filter(organisation_id=user.organisation_id)

    def perform_create(self, serializer):
        item = serializer.save(
            organisation_id=self.request.user.organisation_id,
            created_by=self.request.user,
            availability_status=AvailabilityStatus.IN_STOCK,
            last_restocked_at=timezone.now(),
        )
        self._audit(self.request, "inventory.create", item)


class PharmacyInventoryDetailView(AuditLogViewMixin, generics.RetrieveUpdateDestroyAPIView):
    audit_entity_type = "inventory_item"
    permission_classes = [IsAuthenticated, IsPharmacyInventoryManager]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return InventoryUpdateSerializer
        return InventoryItemSerializer

    def get_queryset(self):
        user = self.request.user
        qs = InventoryItem.objects.select_related("product", "organisation")
        if user.is_superuser or is_regulator_user(user):
            return qs
        return qs.filter(organisation_id=user.organisation_id)


class PharmacyAvailabilityView(APIView):
    """Bulk availability snapshot for the pharmacy's live stock."""

    permission_classes = [IsAuthenticated, IsPharmacyStaff]

    def get(self, request):
        if not request.user.organisation_id:
            return Response({"detail": "No organisation linked."}, status=400)
        items = InventoryItem.objects.filter(
            organisation_id=request.user.organisation_id,
            is_active=True,
        ).select_related("product")
        data = [
            {
                "inventory_id": str(i.id),
                "product_id": str(i.product_id),
                "product_name": i.product.name,
                "quantity_on_hand": i.quantity_on_hand,
                "availability_status": i.availability_status,
                "live": i.availability_status == AvailabilityStatus.IN_STOCK
                and i.quantity_on_hand > 0,
            }
            for i in items
        ]
        return Response({"count": len(data), "items": data})


class PharmacyTraceabilityReceiveView(APIView):
    """Receive batch serials into pharmacy custody and stock (Phase 8)."""

    permission_classes = [IsAuthenticated, IsPharmacyInventoryManager]

    def post(self, request):
        from apps.core.api.responses import api_response
        from apps.pharmacies.api.serializers import PharmacyReceiveBatchSerializer
        from apps.pharmacies.traceability_services import pharmacy_receive_batch_serials

        ser = PharmacyReceiveBatchSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        data = pharmacy_receive_batch_serials(
            actor=request.user,
            organisation_id=request.user.organisation_id,
            batch_id=d["batch_id"],
            serial_ids=d.get("serial_ids") or None,
            quantity=d.get("quantity") or 0,
            request=request,
        )
        return api_response(data=data, message="Receipt recorded", status_code=status.HTTP_201_CREATED)


class PharmacyTraceabilityDispenseView(APIView):
    """Dispense a single serial from pharmacy stock (Phase 8)."""

    permission_classes = [IsAuthenticated, IsPharmacyInventoryManager]

    def post(self, request):
        from apps.core.api.responses import api_response
        from apps.pharmacies.api.serializers import PharmacyDispenseSerialSerializer
        from apps.pharmacies.traceability_services import pharmacy_dispense_serial

        ser = PharmacyDispenseSerialSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            serial = pharmacy_dispense_serial(
                actor=request.user,
                organisation_id=request.user.organisation_id,
                serial_number=ser.validated_data["serial_number"],
                request=request,
            )
        except Exception as exc:
            return api_response(message=str(exc), status_code=400)
        return api_response(data={"serial_number": serial.serial_number, "dispensed": True}, message="Dispensed")
