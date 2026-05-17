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

    class Meta:
        verbose_name = "Distributor profile"
        verbose_name_plural = "Distributor profiles"
