from django.db import models

from apps.core.models import NPTTEBaseModel
from apps.organisations.models import Organisation
from apps.pharmacies.models import PharmacyProfile
from apps.products.models import Product


class CitizenVerificationSession(NPTTEBaseModel):
    session_token = models.CharField(max_length=64, unique=True, db_index=True)
    device_fingerprint = models.CharField(max_length=64, db_index=True, blank=True)
    client_ip = models.GenericIPAddressField(null=True, blank=True)
    verification_count = models.PositiveIntegerField(default=0)
    last_verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]


class VerificationHistory(NPTTEBaseModel):
    session = models.ForeignKey(
        CitizenVerificationSession, on_delete=models.CASCADE, related_name="history"
    )
    serial_number = models.CharField(max_length=128, db_index=True)
    outcome = models.CharField(max_length=32, db_index=True)
    verified_at = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ["-verified_at"]


class CitizenFraudReport(NPTTEBaseModel):
    session = models.ForeignKey(
        CitizenVerificationSession, on_delete=models.SET_NULL, null=True, blank=True
    )
    serial_number = models.CharField(max_length=128, blank=True, db_index=True)
    pharmacy_name = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    state = models.CharField(max_length=128, blank=True, db_index=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_reviewed = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["-created_at"]


class PublicRecallNotice(NPTTEBaseModel):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="public_recalls")
    recall_number = models.CharField(max_length=128, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    published_at = models.DateTimeField(db_index=True)
    affected_batch_numbers = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["-published_at"]
