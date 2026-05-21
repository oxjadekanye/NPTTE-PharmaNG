"""Phase 11 — pharmacy live inventory operations."""
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.constants import AvailabilityStatus
from apps.core.permissions import IsPharmacyInventoryManager
from apps.inventory.models import InventoryItem, InventoryMovement


class PharmacyStockMovementView(APIView):
    permission_classes = [IsAuthenticated, IsPharmacyInventoryManager]

    def post(self, request):
        item_id = request.data.get("inventory_item_id")
        movement_type = request.data.get("movement_type", "adjustment")
        delta = int(request.data.get("quantity_delta", 0))
        item = InventoryItem.objects.get(pk=item_id, organisation_id=request.user.organisation_id)
        item.quantity_on_hand = max(0, item.quantity_on_hand + delta)
        if item.quantity_on_hand <= 5:
            item.availability_status = AvailabilityStatus.LOW_STOCK
        elif item.quantity_on_hand == 0:
            item.availability_status = AvailabilityStatus.OUT_OF_STOCK
        else:
            item.availability_status = AvailabilityStatus.IN_STOCK
        item.save(update_fields=["quantity_on_hand", "availability_status", "updated_at"])
        movement = InventoryMovement.objects.create(
            inventory_item=item,
            movement_type=movement_type,
            quantity_delta=delta,
            reference=request.data.get("reference", ""),
            notes=request.data.get("notes", ""),
            created_by=request.user,
        )
        return api_response(
            data={
                "movement_id": str(movement.id),
                "quantity_on_hand": item.quantity_on_hand,
                "availability_status": item.availability_status,
            },
            message="Stock movement recorded",
            status_code=201,
        )


class PharmacyInventorySyncView(APIView):
    """Reconciliation snapshot for pharmacy portal."""

    permission_classes = [IsAuthenticated, IsPharmacyInventoryManager]

    def get(self, request):
        items = InventoryItem.objects.filter(
            organisation_id=request.user.organisation_id, is_active=True
        ).select_related("product")
        low = sum(1 for i in items if i.availability_status == AvailabilityStatus.LOW_STOCK)
        return api_response(
            data={
                "total_skus": items.count(),
                "low_stock_count": low,
                "synced_at": timezone.now().isoformat(),
                "disclaimer": "Demo operational inventory — not live ERP connectivity.",
            },
            message="Inventory sync health",
        )
