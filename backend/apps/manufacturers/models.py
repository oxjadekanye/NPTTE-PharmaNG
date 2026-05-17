from django.db import models

from apps.core.models import NPTTEBaseModel
from apps.organisations.models import Organisation
from apps.products.models import Product, ProductBatch


class ManufacturerProfile(NPTTEBaseModel):
    """National manufacturer registration profile."""

    organisation = models.OneToOneField(
        Organisation,
        on_delete=models.CASCADE,
        related_name="manufacturer_profile",
    )
    gmp_certificate_number = models.CharField(max_length=128, blank=True, db_index=True)
    production_license = models.CharField(max_length=128, blank=True, db_index=True)
    facility_count = models.PositiveIntegerField(default=1)
    compliance_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Manufacturer profile"
        verbose_name_plural = "Manufacturer profiles"


class ManufacturingSite(NPTTEBaseModel):
    """Individual manufacturing facility under a manufacturer organisation."""

    manufacturer = models.ForeignKey(
        ManufacturerProfile,
        on_delete=models.CASCADE,
        related_name="sites",
    )
    site_name = models.CharField(max_length=255)
    site_code = models.CharField(max_length=64, db_index=True)
    address_line_1 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=128, blank=True)
    state = models.CharField(max_length=128, blank=True, db_index=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        unique_together = [("manufacturer", "site_code")]
        verbose_name = "Manufacturing site"
        verbose_name_plural = "Manufacturing sites"


class ProductionLicense(NPTTEBaseModel):
    license_number = models.CharField(max_length=128, unique=True, db_index=True)
    manufacturer = models.ForeignKey(
        ManufacturerProfile,
        on_delete=models.CASCADE,
        related_name="production_licenses",
    )
    issued_at = models.DateField()
    expires_at = models.DateField(null=True, blank=True, db_index=True)
    issuing_authority = models.CharField(max_length=128, default="NAFDAC")

    class Meta:
        ordering = ["-issued_at"]


class GMPComplianceRecord(NPTTEBaseModel):
    manufacturer = models.ForeignKey(
        ManufacturerProfile,
        on_delete=models.CASCADE,
        related_name="gmp_records",
    )
    inspection_date = models.DateField(db_index=True)
    is_compliant = models.BooleanField(default=True, db_index=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    findings = models.TextField(blank=True)
    inspector_reference = models.CharField(max_length=128, blank=True)

    class Meta:
        ordering = ["-inspection_date"]


class ManufacturingAudit(NPTTEBaseModel):
    manufacturer = models.ForeignKey(
        ManufacturerProfile,
        on_delete=models.CASCADE,
        related_name="manufacturing_audits",
    )
    site = models.ForeignKey(
        ManufacturingSite,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audits",
    )
    audit_type = models.CharField(max_length=64, db_index=True)
    outcome = models.CharField(max_length=64, blank=True)
    notes = models.TextField(blank=True)
    audited_at = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ["-audited_at"]


class RecallNotice(NPTTEBaseModel):
    """Manufacturer-initiated recall notice linked to national batch registry."""

    manufacturer = models.ForeignKey(
        ManufacturerProfile,
        on_delete=models.PROTECT,
        related_name="recall_notices",
    )
    batch = models.ForeignKey(
        ProductBatch,
        on_delete=models.PROTECT,
        related_name="recall_notices",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="recall_notices",
    )
    reason = models.TextField()
    effective_at = models.DateTimeField(db_index=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-effective_at"]
        verbose_name = "Recall notice"
        verbose_name_plural = "Recall notices"
