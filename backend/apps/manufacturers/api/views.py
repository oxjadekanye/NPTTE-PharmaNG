from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.constants import RoleCode
from apps.core.permissions import IsRegulatorUser
from apps.core.roles import get_user_role_code
from apps.manufacturers.api.permissions import IsManufacturerStaff
from apps.manufacturers.api.serializers import (
    BatchCreateSerializer,
    ManufacturerProfileSerializer,
    ManufacturingSiteSerializer,
    ProductBatchSerializer,
    RecallNoticeSerializer,
)
from apps.manufacturers.models import ManufacturerProfile, ManufacturingSite, RecallNotice
from apps.manufacturers.services import create_national_batch, issue_batch_serials, publish_recall_notice
from apps.products.models import Product, ProductBatch


class ManufacturerProfileView(generics.RetrieveAPIView):
    serializer_class = ManufacturerProfileSerializer
    permission_classes = [IsAuthenticated, IsManufacturerStaff]

    def get_object(self):
        return ManufacturerProfile.objects.select_related("organisation").get(
            organisation_id=self.request.user.organisation_id
        )


class ManufacturingSiteListView(generics.ListCreateAPIView):
    serializer_class = ManufacturingSiteSerializer
    permission_classes = [IsAuthenticated, IsManufacturerStaff]

    def get_queryset(self):
        profile = ManufacturerProfile.objects.get(organisation_id=self.request.user.organisation_id)
        return ManufacturingSite.objects.filter(manufacturer=profile, is_active=True)

    def perform_create(self, serializer):
        profile = ManufacturerProfile.objects.get(organisation_id=self.request.user.organisation_id)
        serializer.save(manufacturer=profile, created_by=self.request.user)


class BatchListView(generics.ListAPIView):
    serializer_class = ProductBatchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if get_user_role_code(user) == RoleCode.MANUFACTURER and user.organisation_id:
            return ProductBatch.objects.filter(
                manufacturing_site__manufacturer__organisation_id=user.organisation_id
            ).select_related("product", "manufacturing_site")
        from apps.core.roles import is_regulator_user

        if user.is_superuser or is_regulator_user(user):
            return ProductBatch.objects.select_related("product", "manufacturing_site").order_by("-created_at")[:200]
        return ProductBatch.objects.none()


class BatchCreateView(APIView):
    permission_classes = [IsAuthenticated, IsManufacturerStaff]

    def post(self, request):
        ser = BatchCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        site = ManufacturingSite.objects.get(id=d["manufacturing_site_id"])
        product = Product.objects.get(id=d["product_id"])
        batch = create_national_batch(
            product=product,
            batch_number=d["batch_number"],
            manufacturing_site=site,
            quantity_produced=d["quantity_produced"],
            manufacturing_date=d.get("manufacturing_date"),
            expiry_date=d.get("expiry_date"),
            actor=request.user,
            request=request,
        )
        serials = []
        if d.get("issue_serial_count", 0) > 0:
            serials = issue_batch_serials(batch=batch, count=d["issue_serial_count"], actor=request.user)
        return api_response(
            data={
                "batch": ProductBatchSerializer(batch).data,
                "serials_issued": len(serials),
                "serial_range": [batch.serial_range_start, batch.serial_range_end],
            },
            message="National batch created",
            status_code=status.HTTP_201_CREATED,
        )


class RecallNoticeCreateView(generics.CreateAPIView):
    serializer_class = RecallNoticeSerializer
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
