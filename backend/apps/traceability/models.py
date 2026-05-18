"""
National supply chain transaction records — immutable movement audit trail.
"""
from django.conf import settings
from django.db import models

from apps.core.constants import (
    BatchRegulatoryAuditAction,
    RiskLevel,
    SupplyChainTransactionType,
    VerificationStatus,
)
from apps.core.models import NPTTEBaseModel
from apps.organisations.models import Organisation
from apps.products.models import Product, ProductBatch
from apps.serialization.models import ProductSerial


class SupplyChainTransaction(NPTTEBaseModel):
    """
    Immutable national transaction log for every medication movement.

    `audit_reference` is the immutable public trace identifier (separate from PK).
    """

    audit_reference = models.UUIDField(unique=True, editable=False, db_index=True)
    transaction_type = models.CharField(
        max_length=64,
        choices=SupplyChainTransactionType.CHOICES,
        db_index=True,
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supply_chain_transactions",
    )
    source_organisation = models.ForeignKey(
        Organisation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="outbound_transactions",
    )
    destination_organisation = models.ForeignKey(
        Organisation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inbound_transactions",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supply_chain_transactions",
    )
    batch = models.ForeignKey(
        ProductBatch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supply_chain_transactions",
    )
    product_serial = models.ForeignKey(
        ProductSerial,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supply_chain_transactions",
    )
    quantity_delta = models.IntegerField(
        default=0,
        help_text="Signed quantity change (+ in, - out).",
    )
    verification_status = models.CharField(
        max_length=32,
        choices=VerificationStatus.CHOICES,
        default=VerificationStatus.PENDING,
        db_index=True,
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    device_metadata = models.JSONField(default=dict, blank=True)
    product_metadata = models.JSONField(default=dict, blank=True)
    batch_metadata = models.JSONField(default=dict, blank=True)
    parent_transaction = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="child_transactions",
    )
    risk_level = models.CharField(
        max_length=16,
        choices=RiskLevel.CHOICES,
        default=RiskLevel.LOW,
        db_index=True,
    )
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_immutable = models.BooleanField(default=True, db_index=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Supply chain transaction"
        verbose_name_plural = "Supply chain transactions"
        indexes = [
            models.Index(fields=["transaction_type", "created_at"]),
            models.Index(fields=["source_organisation", "created_at"]),
            models.Index(fields=["destination_organisation", "created_at"]),
            models.Index(fields=["product", "transaction_type"]),
            models.Index(fields=["verification_status", "risk_level"]),
        ]

    def __str__(self):
        return f"{self.audit_reference} — {self.transaction_type}"


class BatchRegulatoryAudit(NPTTEBaseModel):
    """
    Immutable regulator action trail per batch (Phase 8).

    Complements platform AuditLog with domain-specific batch workflow history.
    """

    batch = models.ForeignKey(
        ProductBatch,
        on_delete=models.CASCADE,
        related_name="regulatory_audits",
    )
    action = models.CharField(max_length=64, choices=BatchRegulatoryAuditAction.CHOICES, db_index=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="batch_regulatory_audits",
    )
    notes = models.TextField(blank=True)
    payload = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Batch regulatory audit"
        verbose_name_plural = "Batch regulatory audits"
        indexes = [
            models.Index(fields=["batch", "created_at"]),
        ]

    def __str__(self):
        return f"{self.batch_id} — {self.action}"


class BatchRecall(NPTTEBaseModel):
    """National batch recall registry."""

    batch = models.ForeignKey(ProductBatch, on_delete=models.PROTECT, related_name="recalls")
    recall_reason = models.TextField()
    issued_by_organisation = models.ForeignKey(
        Organisation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issued_recalls",
    )
    effective_at = models.DateTimeField(db_index=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-effective_at"]
        verbose_name = "Batch recall"
        verbose_name_plural = "Batch recalls"


class SerialCustodyEvent(NPTTEBaseModel):
    """Sovereign chain-of-custody ledger per serial (Phase 10)."""

    NODE_MANUFACTURER = "manufacturer"
    NODE_DISTRIBUTOR = "distributor"
    NODE_WAREHOUSE = "warehouse"
    NODE_CUSTOMS = "customs"
    NODE_PHARMACY = "pharmacy"
    NODE_HOSPITAL = "hospital"
    NODE_PATIENT = "patient"
    NODE_CHOICES = [
        (NODE_MANUFACTURER, "Manufacturer"),
        (NODE_DISTRIBUTOR, "Distributor"),
        (NODE_WAREHOUSE, "Warehouse"),
        (NODE_CUSTOMS, "Customs"),
        (NODE_PHARMACY, "Pharmacy"),
        (NODE_HOSPITAL, "Hospital"),
        (NODE_PATIENT, "Patient"),
    ]

    product_serial = models.ForeignKey(
        ProductSerial,
        on_delete=models.CASCADE,
        related_name="custody_events",
    )
    source_node = models.CharField(max_length=32, choices=NODE_CHOICES, blank=True)
    destination_node = models.CharField(max_length=32, choices=NODE_CHOICES, db_index=True)
    source_organisation = models.ForeignKey(
        Organisation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="custody_events_out",
    )
    destination_organisation = models.ForeignKey(
        Organisation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="custody_events_in",
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    verification_signature = models.CharField(max_length=256, blank=True)
    custody_confirmed = models.BooleanField(default=False, db_index=True)
    integrity_status = models.CharField(max_length=32, default="pending", db_index=True)
    supply_chain_transaction = models.ForeignKey(
        SupplyChainTransaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="custody_events",
    )

    class Meta:
        ordering = ["created_at"]
        indexes = [models.Index(fields=["product_serial", "created_at"])]


class RecallExecutionCampaign(NPTTEBaseModel):
    """Nationwide recall propagation and completion tracking (Phase 10)."""

    batch_recall = models.ForeignKey(
        BatchRecall,
        on_delete=models.CASCADE,
        related_name="execution_campaigns",
    )
    campaign_code = models.CharField(max_length=64, unique=True, db_index=True)
    status = models.CharField(max_length=32, default="active", db_index=True)
    pharmacies_targeted = models.PositiveIntegerField(default=0)
    pharmacies_acknowledged = models.PositiveIntegerField(default=0)
    estimated_patient_exposure = models.PositiveIntegerField(default=0)
    destruction_verified = models.BooleanField(default=False)
    quarantine_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]


class PharmacyRecallAcknowledgement(NPTTEBaseModel):
    campaign = models.ForeignKey(
        RecallExecutionCampaign,
        on_delete=models.CASCADE,
        related_name="pharmacy_acks",
    )
    pharmacy_organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name="recall_acknowledgements",
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    completion_pct = models.PositiveSmallIntegerField(default=0)
