from django.db import models

from apps.core.models import NPTTEBaseModel
from apps.organisations.models import Organisation


class DistributorProfile(NPTTEBaseModel):
    organisation = models.OneToOneField(
        Organisation,
        on_delete=models.CASCADE,
        related_name="distributor_profile",
    )
    wholesale_license = models.CharField(max_length=128, blank=True, db_index=True)
    cold_chain_capable = models.BooleanField(default=False)
    coverage_states = models.JSONField(default=list, blank=True)
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Distributor profile"
        verbose_name_plural = "Distributor profiles"


class Warehouse(NPTTEBaseModel):
    """Distributor or manufacturer warehouse facility."""

    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name="warehouses",
    )
    distributor = models.ForeignKey(
        DistributorProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="warehouses",
    )
    name = models.CharField(max_length=255)
    warehouse_code = models.CharField(max_length=64, db_index=True)
    state = models.CharField(max_length=128, blank=True, db_index=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    cold_chain_enabled = models.BooleanField(default=False)

    class Meta:
        unique_together = [("organisation", "warehouse_code")]
        verbose_name = "Warehouse"
        verbose_name_plural = "Warehouses"
