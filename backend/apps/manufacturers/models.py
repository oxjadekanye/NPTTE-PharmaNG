from django.db import models

from apps.core.models import NPTTEBaseModel
from apps.organisations.models import Organisation


class ManufacturerProfile(NPTTEBaseModel):
    organisation = models.OneToOneField(
        Organisation,
        on_delete=models.CASCADE,
        related_name="manufacturer_profile",
    )
    gmp_certificate_number = models.CharField(max_length=128, blank=True, db_index=True)
    production_license = models.CharField(max_length=128, blank=True, db_index=True)
    facility_count = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Manufacturer profile"
        verbose_name_plural = "Manufacturer profiles"
