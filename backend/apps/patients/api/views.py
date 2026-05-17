"""Patient medication search API views."""
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.services import log_api_action
from apps.core.api.mixins import AuditLogViewMixin
from apps.core.permissions import IsPatientUser, IsRegulatorUser
from apps.core.roles import get_user_role_code, is_regulator_user
from apps.core.constants import RoleCode
from apps.patients.api.serializers import (
    MedicationSearchRequestSerializer,
    MedicationSearchSerializer,
    PatientProfileSerializer,
    ProductCatalogSearchSerializer,
    ProductSearchResultSerializer,
)
from apps.patients.models import MedicationSearchRequest, PatientProfile
from apps.patients.services import find_pharmacies_with_stock, run_medication_search


class PatientProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = PatientProfileSerializer
    permission_classes = [IsAuthenticated, IsPatientUser]

    def get_object(self):
        profile, _ = PatientProfile.objects.get_or_create(
            user=self.request.user,
            defaults={
                "preferred_name": self.request.user.get_full_name() or self.request.user.username,
                "phone_number": self.request.user.phone_number,
            },
        )
        return profile


class ProductCatalogSearchView(APIView):
    """Search medicine catalogue before location-based availability lookup."""

    permission_classes = [AllowAny]

    def get(self, request):
        serializer = ProductCatalogSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        products = serializer.get_products()
        return Response(ProductSearchResultSerializer(products, many=True).data)


class MedicationSearchView(AuditLogViewMixin, APIView):
    """
    Search nearby pharmacies with medication in stock.

    Patients must consent to location search when authenticated.
    """

    audit_entity_type = "medication_search"
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = MedicationSearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        patient = None
        if request.user.is_authenticated:
            role = get_user_role_code(request.user)
            if role == RoleCode.PATIENT:
                patient, _ = PatientProfile.objects.get_or_create(user=request.user)
                if not patient.consent_to_location_search:
                    return Response(
                        {
                            "detail": "Location search consent required. "
                            "Enable consent_to_location_search on your profile."
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )

        search_request, pharmacies, products = run_medication_search(
            latitude=data["latitude"],
            longitude=data["longitude"],
            radius_miles=data["radius_miles"],
            patient=patient,
            product_id=data.get("product_id"),
            search_term=data.get("search_term", ""),
            medicine_name=data.get("medicine_name", ""),
            dosage=data.get("dosage", ""),
            formulation=data.get("formulation", ""),
            generic_name=data.get("generic_name", ""),
            brand_name=data.get("brand_name", ""),
        )

        if not products:
            return Response(
                {
                    "detail": "No matching medicines found in the national catalogue.",
                    "pharmacies": [],
                    "products": [],
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        log_api_action(
            request=request,
            action="patient.medication_search",
            entity_type="medication_search",
            entity_id=search_request.id if search_request else None,
            after_state={
                "result_count": len(pharmacies),
                "radius_miles": str(data["radius_miles"]),
            },
        )

        return Response(
            {
                "search_id": str(search_request.id) if search_request else None,
                "search_status": search_request.search_status if search_request else "completed",
                "matched_products": ProductSearchResultSerializer(products, many=True).data,
                "result_count": len(pharmacies),
                "pharmacies": pharmacies,
            },
            status=status.HTTP_200_OK,
        )


class NearbyPharmaciesView(APIView):
    """Nearby pharmacies with stock for a known product."""

    permission_classes = [AllowAny]

    def get(self, request):
        try:
            lat = request.query_params["latitude"]
            lon = request.query_params["longitude"]
            product_id = request.query_params["product_id"]
            radius = request.query_params.get("radius_miles", "5")
        except KeyError as exc:
            return Response(
                {"detail": f"Missing parameter: {exc.args[0]}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from decimal import Decimal

        pharmacies = find_pharmacies_with_stock(
            product_id=product_id,
            latitude=Decimal(lat),
            longitude=Decimal(lon),
            radius_miles=Decimal(radius),
        )
        return Response({"result_count": len(pharmacies), "pharmacies": pharmacies})


class MedicationSearchHistoryView(generics.ListAPIView):
    serializer_class = MedicationSearchRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if is_regulator_user(user):
            return MedicationSearchRequest.objects.select_related("product", "patient").order_by(
                "-created_at"
            )[:100]
        if get_user_role_code(user) == RoleCode.PATIENT:
            profile = PatientProfile.objects.filter(user=user).first()
            if not profile:
                return MedicationSearchRequest.objects.none()
            return MedicationSearchRequest.objects.filter(patient=profile).select_related(
                "product"
            )
        return MedicationSearchRequest.objects.none()


class MedicationSearchDetailView(generics.RetrieveAPIView):
    serializer_class = MedicationSearchRequestSerializer
    permission_classes = [IsAuthenticated]
    queryset = MedicationSearchRequest.objects.select_related("product", "patient")

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        if is_regulator_user(user):
            return obj
        if get_user_role_code(user) == RoleCode.PATIENT:
            if obj.patient and obj.patient.user_id == user.id:
                return obj
        from rest_framework.exceptions import PermissionDenied

        raise PermissionDenied("You may not access this search record.")
