from rest_framework import serializers

from apps.traceability.models import BatchRecall, BatchRegulatoryAudit, SupplyChainTransaction


class SupplyChainTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplyChainTransaction
        fields = (
            "id",
            "audit_reference",
            "transaction_type",
            "actor",
            "source_organisation",
            "destination_organisation",
            "product",
            "batch",
            "product_serial",
            "quantity_delta",
            "verification_status",
            "latitude",
            "longitude",
            "device_metadata",
            "product_metadata",
            "batch_metadata",
            "parent_transaction",
            "risk_level",
            "risk_score",
            "notes",
            "created_at",
        )
        read_only_fields = fields


class SupplyChainTransactionCreateSerializer(serializers.Serializer):
    transaction_type = serializers.CharField(max_length=64)
    source_organisation_id = serializers.UUIDField(required=False, allow_null=True)
    destination_organisation_id = serializers.UUIDField(required=False, allow_null=True)
    product_id = serializers.UUIDField(required=False, allow_null=True)
    batch_id = serializers.UUIDField(required=False, allow_null=True)
    product_serial_id = serializers.UUIDField(required=False, allow_null=True)
    quantity_delta = serializers.IntegerField(default=0)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)


class BatchRecallSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchRecall
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "created_by")


class BatchRegulatoryAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchRegulatoryAudit
        fields = (
            "id",
            "batch",
            "action",
            "actor",
            "notes",
            "payload",
            "created_at",
        )
        read_only_fields = fields
