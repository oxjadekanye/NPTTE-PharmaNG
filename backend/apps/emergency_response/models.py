from django.db import models

from apps.core.constants import EmergencyMode
from apps.core.models import NPTTEBaseModel
from apps.organisations.models import Organisation
from apps.products.models import Product


class NationalEmergencyProtocol(NPTTEBaseModel):
    protocol_code = models.CharField(max_length=64, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    mode = models.CharField(max_length=16, choices=EmergencyMode.CHOICES, default=EmergencyMode.NORMAL, db_index=True)
    activated_at = models.DateTimeField(null=True, blank=True, db_index=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]


class EmergencyMedicineAllocation(NPTTEBaseModel):
    protocol = models.ForeignKey(
        NationalEmergencyProtocol, on_delete=models.CASCADE, related_name="allocations"
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="emergency_allocations")
    target_state = models.CharField(max_length=128, db_index=True)
    quantity_allocated = models.PositiveIntegerField(default=0)
    priority_rank = models.PositiveIntegerField(default=1, db_index=True)

    class Meta:
        ordering = ["priority_rank"]


class CrisisDistributionPlan(NPTTEBaseModel):
    protocol = models.ForeignKey(
        NationalEmergencyProtocol, on_delete=models.CASCADE, related_name="distribution_plans"
    )
    plan_name = models.CharField(max_length=255)
    coverage_states = models.JSONField(default=list, blank=True)
    is_active_plan = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]


class EmergencyStockTransfer(NPTTEBaseModel):
    plan = models.ForeignKey(
        CrisisDistributionPlan, on_delete=models.CASCADE, related_name="transfers"
    )
    source_organisation = models.ForeignKey(
        Organisation, on_delete=models.PROTECT, related_name="emergency_transfers_out"
    )
    destination_organisation = models.ForeignKey(
        Organisation, on_delete=models.PROTECT, related_name="emergency_transfers_in"
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=0)
    transferred_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
