from rest_framework import serializers

from apps.emergency.models import EmergencyMedicineWatchlist


class EmergencyWatchlistSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = EmergencyMedicineWatchlist
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "created_by")
