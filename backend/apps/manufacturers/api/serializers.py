from rest_framework import serializers

from apps.manufacturers.models import (
    GMPComplianceRecord,
    ManufacturerProfile,
    ManufacturingAudit,
    ManufacturingSite,
    ProductionLicense,
    RecallNotice,
)
from apps.products.models import ProductBatch


class ManufacturingSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManufacturingSite
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "created_by")


class ManufacturerProfileSerializer(serializers.ModelSerializer):
    organisation_name = serializers.CharField(source="organisation.legal_name", read_only=True)

    class Meta:
        model = ManufacturerProfile
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "created_by", "compliance_score")


class ProductBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductBatch
        fields = "__all__"
        read_only_fields = ("id", "verification_hash", "created_at", "updated_at", "created_by")


class BatchCreateSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    batch_number = serializers.CharField(max_length=128)
    manufacturing_site_id = serializers.UUIDField()
    quantity_produced = serializers.IntegerField(min_value=1)
    manufacturing_date = serializers.DateField(required=False)
    expiry_date = serializers.DateField(required=False)
    issue_serial_count = serializers.IntegerField(min_value=0, max_value=10000, default=0)


class RecallNoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecallNotice
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "created_by")
