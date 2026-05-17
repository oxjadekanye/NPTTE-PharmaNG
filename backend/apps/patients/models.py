"""
Patient profile and medication search request models.
"""
from django.conf import settings
from django.db import models

from apps.core.constants import MedicationSearchStatus
from apps.core.models import NPTTEBaseModel
from apps.products.models import Product


class PatientProfile(NPTTEBaseModel):
    """
    Patient platform profile (optional link to authenticated user).

    Stores consent and contact preferences for medication search services.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="patient_profile",
    )
    preferred_name = models.CharField(max_length=128, blank=True)
    phone_number = models.CharField(max_length=32, blank=True, db_index=True)
    consent_to_location_search = models.BooleanField(
        default=False,
        help_text="Patient must consent before location-based pharmacy search.",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Patient profile"
        verbose_name_plural = "Patient profiles"

    def __str__(self):
        return self.preferred_name or str(self.id)


class MedicationSearchRequest(NPTTEBaseModel):
    """
    Patient medication availability search request.

    Captures product, patient location, and search radius for matching
    pharmacies with in-stock inventory. Processing is delegated to services.
    """

    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        related_name="medication_searches",
        null=True,
        blank=True,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="medication_searches",
    )
    search_term = models.CharField(
        max_length=255,
        blank=True,
        help_text="Free-text search input when product is resolved separately.",
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    radius_miles = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=5,
        help_text="Search radius from patient location in miles.",
    )
    search_status = models.CharField(
        max_length=32,
        choices=MedicationSearchStatus.CHOICES,
        default=MedicationSearchStatus.PENDING,
        db_index=True,
    )
    result_count = models.PositiveIntegerField(default=0)
    results_snapshot = models.JSONField(
        default=list,
        blank=True,
        help_text="Cached pharmacy matches (foundation — replaced by API responses later).",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Medication search request"
        verbose_name_plural = "Medication search requests"
        indexes = [
            models.Index(fields=["search_status", "created_at"]),
        ]

    def __str__(self):
        return f"Search {self.id} — {self.product}"


class SavedMedication(NPTTEBaseModel):
    """Patient saved medication for history and refill tracking."""

    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        related_name="saved_medications",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="saved_by_patients",
    )
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = [("patient", "product")]
        verbose_name = "Saved medication"
        verbose_name_plural = "Saved medications"


class MedicationReminder(NPTTEBaseModel):
    """Refill reminder for patient medication adherence."""

    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        related_name="medication_reminders",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="refill_reminders",
    )
    remind_at = models.DateTimeField(db_index=True)
    is_sent = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["remind_at"]
        verbose_name = "Medication reminder"
        verbose_name_plural = "Medication reminders"
