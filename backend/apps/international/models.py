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
