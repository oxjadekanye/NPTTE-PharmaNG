from django.db import models

from apps.core.models import TimestampedModel, UUIDPrimaryKeyModel


class BlockchainAnchor(UUIDPrimaryKeyModel, TimestampedModel):
    """Pending/completed anchor of audit or transaction hash to distributed ledger."""

    entity_type = models.CharField(max_length=128, db_index=True)
    entity_id = models.UUIDField(db_index=True)
    payload_hash = models.CharField(max_length=128, db_index=True)
    network = models.CharField(max_length=64, default="hyperledger-fabric")
    anchor_status = models.CharField(max_length=32, default="pending", db_index=True)
    transaction_id = models.CharField(max_length=255, blank=True)
    anchored_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["entity_type", "entity_id"]),
            models.Index(fields=["anchor_status", "created_at"]),
        ]
