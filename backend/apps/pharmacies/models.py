"""
Pharmacy profile models.
"""
from django.db import models

from apps.core.models import NPTTEBaseModel
from apps.organisations.models import Organisation


class PharmacyProfile(NPTTEBaseModel):
    """
    Pharmacy-specific profile linked to a registered organisation.

    Geolocation fields support radius-based patient medication search.
    """

    organisation = models.OneToOneField(
        Organisation,
        on_delete=models.CASCADE,
        related_name="pharmacy_profile",
    )
    pharmacy_license_number = models.CharField(max_length=128, db_index=True)
    superintendent_pharmacist_name = models.CharField(max_length=255, blank=True)
    opening_hours = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured weekly opening hours (e.g. day keys with open/close times).",
    )
    supports_delivery = models.BooleanField(default=False)
    supports_emergency_supply = models.BooleanField(default=False)
    is_national_registry_verified = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Verified on NPTTE national pharmacy registry.",
    )
    parent_branch = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="branches",
    )

    class Meta:
        ordering = ["organisation__legal_name"]
        verbose_name = "Pharmacy profile"
        verbose_name_plural = "Pharmacy profiles"

    def __str__(self):
        return self.organisation.legal_name
