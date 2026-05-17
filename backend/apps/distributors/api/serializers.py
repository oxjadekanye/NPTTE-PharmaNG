from rest_framework import serializers

from apps.distributors.models import DistributorProfile, Warehouse


class DistributorProfileSerializer(serializers.ModelSerializer):
    organisation_name = serializers.CharField(source="organisation.legal_name", read_only=True)

    class Meta:
        model = DistributorProfile
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "created_by", "risk_score")


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "created_by")
