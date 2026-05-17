from rest_framework import serializers

from apps.prescriptions.models import (
    DispensingRecord,
    PrescribingDoctor,
    Prescription,
    PrescriptionItem,
    RefillAuthorization,
)


class PrescribingDoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescribingDoctor
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "created_by")


class PrescriptionItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = PrescriptionItem
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "created_by")


class PrescriptionSerializer(serializers.ModelSerializer):
    items = PrescriptionItemSerializer(many=True, read_only=True)
    patient_name = serializers.CharField(source="patient.user.get_full_name", read_only=True)

    class Meta:
        model = Prescription
        fields = "__all__"
        read_only_fields = ("id", "risk_score", "created_at", "updated_at", "created_by")


class PrescriptionCreateSerializer(serializers.Serializer):
    prescription_number = serializers.CharField(max_length=128)
    patient_id = serializers.UUIDField()
    prescribing_doctor_id = serializers.UUIDField(required=False, allow_null=True)
    product_id = serializers.UUIDField(required=False, allow_null=True)
    dosage_instructions = serializers.CharField(required=False, allow_blank=True)
    quantity_prescribed = serializers.IntegerField(min_value=1, default=1)
    is_controlled_substance = serializers.BooleanField(default=False)
    items = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text="Optional line items: product_id, quantity, dosage_instructions",
    )


class DispensingRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = DispensingRecord
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "created_by")


class DispenseSerializer(serializers.Serializer):
    product_serial_id = serializers.UUIDField(required=False, allow_null=True)
    quantity_dispensed = serializers.IntegerField(min_value=1, default=1)


class RefillAuthorizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefillAuthorization
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "created_by", "refills_used")
