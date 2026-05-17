"""
Organisation and organisation type models.
"""
from django.db import models

from apps.core.models import NPTTEBaseModel


class OrganisationType(NPTTEBaseModel):
    """
    Classification of organisations in the Nigerian pharmaceutical ecosystem.

    Examples: manufacturer, importer, distributor, pharmacy, hospital, regulator.
    """

    code = models.CharField(max_length=64, unique=True, db_index=True)
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Organisation type"
        verbose_name_plural = "Organisation types"

    def __str__(self):
        return self.name


class Organisation(NPTTEBaseModel):
    """
    Registered organisation participating in NPTTE.

    Holds licensing references and geographic anchors for supply chain traceability.
    """

    organisation_type = models.ForeignKey(
        OrganisationType,
        on_delete=models.PROTECT,
        related_name="organisations",
    )
    legal_name = models.CharField(max_length=255, db_index=True)
    trading_name = models.CharField(max_length=255, blank=True)
    registration_number = models.CharField(max_length=128, blank=True, db_index=True)
    license_number = models.CharField(max_length=128, blank=True, db_index=True)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=32, blank=True)
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=128, blank=True)
    state = models.CharField(max_length=128, blank=True, db_index=True)
    country = models.CharField(max_length=2, default="NG")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        ordering = ["legal_name"]
        verbose_name = "Organisation"
        verbose_name_plural = "Organisations"
        indexes = [
            models.Index(fields=["state", "city"]),
        ]

    def __str__(self):
        return self.trading_name or self.legal_name
