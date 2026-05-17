from rest_framework import serializers

from apps.alerts.models import NationalAlert


class NationalAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = NationalAlert
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "created_by")
