from rest_framework import serializers

from apps.logistics.models import (
    ColdChainLog,
    DeliveryConfirmation,
    LogisticsShipment,
    ShipmentCheckpoint,
    ShipmentItem,
)


class ShipmentItemSerializer(serializers.ModelSerializer):
    batch_number = serializers.CharField(source="batch.batch_number", read_only=True)

    class Meta:
        model = ShipmentItem
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "created_by")


class LogisticsShipmentSerializer(serializers.ModelSerializer):
    items = ShipmentItemSerializer(many=True, read_only=True)

    class Meta:
        model = LogisticsShipment
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "created_by", "supply_chain_transaction")


class ShipmentCreateSerializer(serializers.Serializer):
    tracking_number = serializers.CharField(max_length=128)
    origin_organisation_id = serializers.UUIDField()
    destination_organisation_id = serializers.UUIDField()
    temperature_controlled = serializers.BooleanField(default=False)
    batch_ids = serializers.ListField(child=serializers.UUIDField(), required=False)


class CheckpointSerializer(serializers.Serializer):
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    temperature_celsius = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False, allow_null=True
    )
    condition_notes = serializers.CharField(required=False, allow_blank=True)


class DeliveryConfirmSerializer(serializers.Serializer):
    received_by_name = serializers.CharField(max_length=255)
    quantity_received = serializers.IntegerField(min_value=0)
    rejection_reason = serializers.CharField(required=False, allow_blank=True)
