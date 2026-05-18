from rest_framework import serializers

from apps.manufacturers.api.serializers import ProductBatchSerializer
from apps.products.models import ProductBatch


class BatchApprovalSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True)


class BatchRejectSerializer(serializers.Serializer):
    reason = serializers.CharField(required=True)


class BatchSuspendSerializer(serializers.Serializer):
    reason = serializers.CharField(required=True)


class NationalBatchRecallSerializer(serializers.Serializer):
    reason = serializers.CharField(required=True)
    issued_by_organisation_id = serializers.UUIDField(required=False, allow_null=True)


class PendingBatchSerializer(ProductBatchSerializer):
    manufacturer_name = serializers.CharField(
        source="manufacturing_site.manufacturer.organisation.legal_name",
        read_only=True,
        allow_null=True,
    )
