from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.permissions import IsHospitalStaff, IsPharmacyStaff, IsRegulatorUser
from apps.core.roles import get_user_role_code, is_regulator_user
from apps.core.constants import RoleCode
from apps.patients.models import PatientProfile
from apps.prescriptions.api.serializers import (
    DispenseSerializer,
    DispensingRecordSerializer,
    PrescriptionCreateSerializer,
    PrescriptionSerializer,
    RefillAuthorizationSerializer,
)
from apps.prescriptions.models import DispensingRecord, Prescription, PrescriptionItem, RefillAuthorization
from apps.prescriptions.services import calculate_prescription_risk


class PrescriptionListCreateView(generics.ListCreateAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsHospitalStaff()]

    def get_queryset(self):
        user = self.request.user
        qs = Prescription.objects.select_related(
            "patient",
            "patient__user",
            "prescriber_organisation",
            "prescribing_doctor",
        ).prefetch_related("items")
        if is_regulator_user(user):
            return qs.order_by("-issued_at")[:200]
        if get_user_role_code(user) == RoleCode.PATIENT:
            return qs.filter(patient__user=user)
        if user.organisation_id:
            return qs.filter(prescriber_organisation_id=user.organisation_id)
        return qs.none()

    def create(self, request, *args, **kwargs):
        ser = PrescriptionCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        patient = PatientProfile.objects.get(pk=d["patient_id"])
        rx = Prescription.objects.create(
            prescription_number=d["prescription_number"],
            patient=patient,
            prescriber_organisation_id=request.user.organisation_id,
            prescribing_doctor_id=d.get("prescribing_doctor_id"),
            product_id=d.get("product_id"),
            dosage_instructions=d.get("dosage_instructions", ""),
            quantity_prescribed=d.get("quantity_prescribed", 1),
            is_controlled_substance=d.get("is_controlled_substance", False),
            issued_at=timezone.now(),
            created_by=request.user,
        )
        for item in d.get("items", []):
            PrescriptionItem.objects.create(
                prescription=rx,
                product_id=item["product_id"],
                quantity=item.get("quantity", 1),
                dosage_instructions=item.get("dosage_instructions", ""),
                created_by=request.user,
            )
        calculate_prescription_risk(prescription=rx)
        return api_response(
            data=PrescriptionSerializer(rx).data,
            message="Prescription issued",
            status_code=status.HTTP_201_CREATED,
        )


class PrescriptionDetailView(generics.RetrieveAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Prescription.objects.prefetch_related("items")


class PrescriptionRiskView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request, pk):
        rx = Prescription.objects.get(pk=pk)
        score = calculate_prescription_risk(prescription=rx)
        return api_response(data={"prescription_id": str(rx.id), "risk_score": str(score)})


class PrescriptionDispenseView(APIView):
    permission_classes = [IsAuthenticated, IsPharmacyStaff]

    def post(self, request, pk):
        rx = Prescription.objects.get(pk=pk)
        ser = DispenseSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        record = DispensingRecord.objects.create(
            prescription=rx,
            pharmacy_id=request.user.organisation_id,
            product_serial_id=d.get("product_serial_id"),
            quantity_dispensed=d["quantity_dispensed"],
            dispensed_at=timezone.now(),
            created_by=request.user,
        )
        rx.is_fulfilled = True
        rx.save(update_fields=["is_fulfilled", "updated_at"])
        calculate_prescription_risk(prescription=rx)
        return api_response(
            data=DispensingRecordSerializer(record).data,
            message="Prescription dispensed",
        )


class RefillAuthorizationView(APIView):
    permission_classes = [IsAuthenticated, IsHospitalStaff]

    def get(self, request, prescription_id):
        refill = RefillAuthorization.objects.filter(prescription_id=prescription_id).first()
        if not refill:
            return api_response(data=None, message="No refill authorization", status_code=status.HTTP_404_NOT_FOUND)
        return api_response(data=RefillAuthorizationSerializer(refill).data)

    def patch(self, request, prescription_id):
        refill, _ = RefillAuthorization.objects.get_or_create(
            prescription_id=prescription_id,
            defaults={"created_by": request.user},
        )
        ser = RefillAuthorizationSerializer(refill, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return api_response(data=ser.data, message="Refill authorization updated")
