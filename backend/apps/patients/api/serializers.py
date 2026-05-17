"""Patient medication search API serializers."""
from decimal import Decimal

from rest_framework import serializers

from apps.patients.models import MedicationSearchRequest, PatientProfile
from apps.patients.services import search_products
from apps.products.models import Product


class PatientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientProfile
        fields = (
            "id",
            "preferred_name",
            "phone_number",
            "consent_to_location_search",
            "status",
            "is_active",
            "created_at",
        )
        read_only_fields = ("id", "created_at", "status")


class ProductSearchResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "brand_name",
            "active_ingredient",
            "strength",
            "dosage_form",
            "pack_size",
        )


class MedicationSearchSerializer(serializers.Serializer):
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    radius_miles = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("5"),
        min_value=Decimal("0.5"),
        max_value=Decimal("50"),
    )
    product_id = serializers.UUIDField(required=False, allow_null=True)
    search_term = serializers.CharField(required=False, allow_blank=True, max_length=255)
    medicine_name = serializers.CharField(required=False, allow_blank=True, max_length=255)
    dosage = serializers.CharField(required=False, allow_blank=True, max_length=64)
    formulation = serializers.CharField(required=False, allow_blank=True, max_length=128)
    generic_name = serializers.CharField(required=False, allow_blank=True, max_length=255)
    brand_name = serializers.CharField(required=False, allow_blank=True, max_length=255)

    def validate(self, attrs):
        has_product = attrs.get("product_id")
        has_text = any(
            attrs.get(k)
            for k in (
                "search_term",
                "medicine_name",
                "dosage",
                "formulation",
                "generic_name",
                "brand_name",
            )
        )
        if not has_product and not has_text:
            raise serializers.ValidationError(
                "Provide product_id or at least one search field."
            )
        return attrs


class MedicationSearchRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicationSearchRequest
        fields = (
            "id",
            "product",
            "search_term",
            "latitude",
            "longitude",
            "radius_miles",
            "search_status",
            "result_count",
            "results_snapshot",
            "created_at",
        )
        read_only_fields = fields


class ProductCatalogSearchSerializer(serializers.Serializer):
    q = serializers.CharField(required=False, allow_blank=True)
    medicine_name = serializers.CharField(required=False, allow_blank=True)
    dosage = serializers.CharField(required=False, allow_blank=True)
    formulation = serializers.CharField(required=False, allow_blank=True)
    generic_name = serializers.CharField(required=False, allow_blank=True)
    brand_name = serializers.CharField(required=False, allow_blank=True)

    def get_products(self):
        return search_products(
            query=self.validated_data.get("q", ""),
            medicine_name=self.validated_data.get("medicine_name", ""),
            dosage=self.validated_data.get("dosage", ""),
            formulation=self.validated_data.get("formulation", ""),
            generic_name=self.validated_data.get("generic_name", ""),
            brand_name=self.validated_data.get("brand_name", ""),
        )
