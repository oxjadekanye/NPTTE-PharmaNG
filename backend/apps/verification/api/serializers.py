from rest_framework import serializers

from apps.verification.models import VerificationEvent, VerificationScanLog


class VerifySerialSerializer(serializers.Serializer):
    serial_number = serializers.CharField(max_length=128, required=False, allow_blank=True)
    barcode = serializers.CharField(max_length=128, required=False, allow_blank=True)
    qr_token = serializers.CharField(max_length=512, required=False, allow_blank=True)
    device_id = serializers.CharField(max_length=128, required=False, allow_blank=True)
    latitude = serializers.DecimalField(
        max_digits=9, decimal_places=6, required=False, allow_null=True
    )
    longitude = serializers.DecimalField(
        max_digits=9, decimal_places=6, required=False, allow_null=True
    )

    def validate(self, attrs):
        if not attrs.get("serial_number") and not attrs.get("barcode") and not attrs.get("qr_token"):
            raise serializers.ValidationError(
                "Provide serial_number, barcode, or qr_token."
            )
        return attrs


class VerificationEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationEvent
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "created_by")


class VerificationScanLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationScanLog
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "created_by")
