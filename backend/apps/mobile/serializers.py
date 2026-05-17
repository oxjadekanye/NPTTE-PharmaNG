"""Lightweight mobile-optimized serializers."""
from rest_framework import serializers

from apps.mobile.models import DeviceRegistration


class MobileDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceRegistration
        fields = ("id", "device_id", "device_type", "trust_score", "last_sync_at", "app_version")
        read_only_fields = fields


class MobileEnvelopeSerializer(serializers.Serializer):
    """Compact API envelope for mobile clients."""
    success = serializers.BooleanField()
    data = serializers.JSONField()
    message = serializers.CharField(required=False, allow_blank=True)
    sync_token = serializers.CharField(required=False, allow_blank=True)
