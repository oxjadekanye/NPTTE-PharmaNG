"""Phase 10 — digital regulatory certificates with QR verification."""
from django.conf import settings
from django.db import models

from apps.core.models import NPTTEBaseModel
from apps.products.models import ProductBatch


class DigitalRegulatoryCertificate(NPTTEBaseModel):
    CERT_BATCH_APPROVAL = "batch_approval"
    CERT_PRODUCT = "product_certification"
    CERT_INSPECTION = "inspection_report"
    CERT_AUTHORIZATION = "regulator_authorization"
    CERT_SERIALIZATION = "serialization_certificate"
    TYPE_CHOICES = [
        (CERT_BATCH_APPROVAL, "Batch approval"),
        (CERT_PRODUCT, "Product certification"),
        (CERT_INSPECTION, "Inspection report"),
        (CERT_AUTHORIZATION, "Regulator authorization"),
        (CERT_SERIALIZATION, "Serialization certificate"),
    ]

    certificate_number = models.CharField(max_length=64, unique=True, db_index=True)
    certificate_type = models.CharField(max_length=64, choices=TYPE_CHOICES, db_index=True)
    batch = models.ForeignKey(
        ProductBatch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="certificates",
    )
    subject_label = models.CharField(max_length=255)
    issued_at = models.DateTimeField(db_index=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    qr_verification_code = models.CharField(max_length=128, unique=True, db_index=True)
    digital_signature = models.CharField(max_length=256)
    tamper_hash = models.CharField(max_length=128, db_index=True)
    payload = models.JSONField(default=dict, blank=True)
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issued_certificates",
    )

    class Meta:
        ordering = ["-issued_at"]
