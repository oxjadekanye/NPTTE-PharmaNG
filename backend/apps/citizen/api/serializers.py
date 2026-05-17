from rest_framework import serializers


class PublicVerifySerializer(serializers.Serializer):
    serial_number = serializers.CharField(max_length=128, required=False, allow_blank=True)
    qr_token = serializers.CharField(max_length=512, required=False, allow_blank=True)
    barcode = serializers.CharField(max_length=128, required=False, allow_blank=True)


class CounterfeitReportSerializer(serializers.Serializer):
    serial_number = serializers.CharField(max_length=128, required=False, allow_blank=True)
    pharmacy_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    description = serializers.CharField()
    state = serializers.CharField(max_length=128, required=False, allow_blank=True)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
