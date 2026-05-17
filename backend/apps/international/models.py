from django.db import models

from apps.core.models import NPTTEBaseModel
from apps.organisations.models import Organisation


class ImportManifest(NPTTEBaseModel):
    manifest_number = models.CharField(max_length=128, unique=True, db_index=True)
    importer = models.ForeignKey(
        Organisation,
        on_delete=models.PROTECT,
        related_name="import_manifests",
    )
    origin_country = models.CharField(max_length=2, db_index=True)
    port_of_entry = models.CharField(max_length=128, blank=True)
    declared_at = models.DateTimeField(db_index=True)
    batch_references = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["-declared_at"]


class ExportManifest(NPTTEBaseModel):
    manifest_number = models.CharField(max_length=128, unique=True, db_index=True)
    exporter = models.ForeignKey(
        Organisation,
        on_delete=models.PROTECT,
        related_name="export_manifests",
    )
    destination_country = models.CharField(max_length=2, db_index=True)
    port_of_exit = models.CharField(max_length=128, blank=True)
    declared_at = models.DateTimeField(db_index=True)
    batch_references = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["-declared_at"]


class BorderVerificationLog(NPTTEBaseModel):
    manifest_type = models.CharField(max_length=16, db_index=True)
    manifest_id = models.UUIDField(db_index=True)
    border_point = models.CharField(max_length=128, db_index=True)
    verification_outcome = models.CharField(max_length=64, db_index=True)
    verified_at = models.DateTimeField(db_index=True)
    officer_reference = models.CharField(max_length=128, blank=True)
    scan_metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-verified_at"]
        verbose_name = "Border verification log"
        verbose_name_plural = "Border verification logs"


class BorderInspectionCheckpoint(NPTTEBaseModel):
    checkpoint_code = models.CharField(max_length=64, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    state = models.CharField(max_length=128, blank=True, db_index=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    supports_ecowas = models.BooleanField(default=True, db_index=True)

    class Meta:
        verbose_name = "Border inspection checkpoint"
        verbose_name_plural = "Border inspection checkpoints"


class InternationalVerificationRequest(NPTTEBaseModel):
    manifest = models.ForeignKey(
        ImportManifest, on_delete=models.CASCADE, related_name="verification_requests"
    )
    checkpoint = models.ForeignKey(
        BorderInspectionCheckpoint, on_delete=models.PROTECT, related_name="verification_requests"
    )
    request_status = models.CharField(max_length=32, db_index=True, default="pending")
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, db_index=True)
    requested_at = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ["-requested_at"]


class ImportRiskAssessment(NPTTEBaseModel):
    manifest = models.OneToOneField(
        ImportManifest, on_delete=models.CASCADE, related_name="risk_assessment"
    )
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, db_index=True)
    suspicious_indicators = models.JSONField(default=list, blank=True)
    assessed_at = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ["-assessed_at"]


class CustomsHoldNotice(NPTTEBaseModel):
    manifest = models.ForeignKey(ImportManifest, on_delete=models.CASCADE, related_name="hold_notices")
    hold_reason = models.TextField()
    issued_at = models.DateTimeField(db_index=True)
    released_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-issued_at"]
