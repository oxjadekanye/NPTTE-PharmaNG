"""Pharmacy API serializers."""
from rest_framework import serializers

from apps.core.constants import AvailabilityStatus
from apps.inventory.models import InventoryItem, InventoryMovement
from apps.organisations.models import Organisation
from apps.pharmacies.models import PharmacyProfile
from apps.products.models import Product


class OrganisationLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = (
            "id",
            "legal_name",
            "trading_name",
            "phone_number",
            "email",
            "address_line_1",
            "address_line_2",
            "city",
            "state",
            "country",
            "latitude",
            "longitude",
        )
        read_only_fields = fields


class PharmacyProfileSerializer(serializers.ModelSerializer):
    organisation = OrganisationLocationSerializer(read_only=True)
    organisation_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = PharmacyProfile
        fields = (
            "id",
            "organisation",
            "organisation_id",
            "pharmacy_license_number",
            "superintendent_pharmacist_name",
            "opening_hours",
            "supports_delivery",
            "supports_emergency_supply",
            "status",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "organisation")


class PharmacyProfileUpdateSerializer(serializers.ModelSerializer):
    latitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=False,
        write_only=True,
    )
    longitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=False,
        write_only=True,
    )
    phone_number = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = PharmacyProfile
        fields = (
            "superintendent_pharmacist_name",
            "opening_hours",
            "supports_delivery",
            "supports_emergency_supply",
            "latitude",
            "longitude",
            "phone_number",
        )

    def update(self, instance, validated_data):
        lat = validated_data.pop("latitude", None)
        lon = validated_data.pop("longitude", None)
        phone = validated_data.pop("phone_number", None)
        org = instance.organisation
        if lat is not None:
            org.latitude = lat
        if lon is not None:
            org.longitude = lon
        if phone is not None:
            org.phone_number = phone
        if lat is not None or lon is not None or phone is not None:
            org.save(update_fields=["latitude", "longitude", "phone_number", "updated_at"])
        return super().update(instance, validated_data)


class ProductBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("id", "name", "brand_name", "active_ingredient", "strength", "dosage_form")


class InventoryItemSerializer(serializers.ModelSerializer):
    product = ProductBriefSerializer(read_only=True)
    product_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = InventoryItem
        fields = (
            "id",
            "organisation",
            "product",
            "product_id",
            "batch",
            "quantity_on_hand",
            "availability_status",
            "last_restocked_at",
            "status",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "organisation", "created_at", "updated_at", "product")


class InventoryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = ("quantity_on_hand", "availability_status", "is_active")

    def validate_quantity_on_hand(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative.")
        return value

    def update(self, instance, validated_data):
        old_qty = instance.quantity_on_hand
        instance = super().update(instance, validated_data)
        delta = instance.quantity_on_hand - old_qty
        if delta != 0:
            InventoryMovement.objects.create(
                inventory_item=instance,
                movement_type="api_adjustment",
                quantity_delta=delta,
                reference="inventory_api_update",
                created_by=self.context["request"].user,
            )
            from apps.core.constants import SupplyChainTransactionType
            from apps.fraud_detection.services import create_fraud_flag, score_inventory_anomaly
            from apps.traceability.services import record_supply_chain_transaction

            txn = record_supply_chain_transaction(
                transaction_type=SupplyChainTransactionType.STOCK_ADJUSTMENT,
                request=self.context["request"],
                actor=self.context["request"].user,
                destination_organisation=instance.organisation,
                product=instance.product,
                batch=instance.batch,
                quantity_delta=delta,
            )
            risk = score_inventory_anomaly(
                organisation=instance.organisation,
                quantity_delta=delta,
            )
            if risk >= 55:
                create_fraud_flag(
                    flag_type="abnormal_inventory_movement",
                    organisation=instance.organisation,
                    supply_chain_transaction=txn,
                    risk_score=risk,
                    description="Large inventory adjustment detected",
                )
        if instance.quantity_on_hand == 0:
            instance.availability_status = AvailabilityStatus.OUT_OF_STOCK
        elif instance.quantity_on_hand <= 10:
            instance.availability_status = AvailabilityStatus.LOW_STOCK
        else:
            instance.availability_status = AvailabilityStatus.IN_STOCK
        instance.save(update_fields=["availability_status", "updated_at"])
        return instance


class PharmacyReceiveBatchSerializer(serializers.Serializer):
    batch_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1, max_value=50000, required=False, default=0)
    serial_ids = serializers.ListField(child=serializers.UUIDField(), required=False, allow_empty=True)

    def validate(self, attrs):
        if not attrs.get("serial_ids") and attrs.get("quantity", 0) < 1:
            raise serializers.ValidationError("Provide quantity or serial_ids.")
        return attrs


class PharmacyDispenseSerialSerializer(serializers.Serializer):
    serial_number = serializers.CharField(max_length=128)
