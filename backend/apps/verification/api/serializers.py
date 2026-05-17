from rest_framework import serializers

from apps.verification.models import VerificationEvent


class VerifySerialSerializer(serializers.Serializer):
    serial_number = serializers.CharField(max_length=128)
    barcode = serializers.CharField(max_length=128, required=False, allow_blank=True)


class VerificationEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationEvent
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "created_by")
