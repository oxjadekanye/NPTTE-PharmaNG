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
    GenerateBatchSerialsSerializer,
    ManufacturerProfileSerializer,
    ManufacturingSiteSerializer,
    ProductBatchSerializer,
    ProductRegisterSerializer,
    RecallNoticeSerializer,
)
from apps.manufacturers.models import ManufacturerProfile, ManufacturingSite, RecallNotice
from apps.manufacturers.services import (
    create_national_batch,
    issue_batch_serials,
    submit_batch_for_regulator_review,
)
from apps.products.models import Product, ProductBatch


class ManufacturerProfileView(generics.RetrieveAPIView):
    serializer_class = ManufacturerProfileSerializer
    permission_classes = [IsAuthenticated, IsManufacturerStaff]

    def get_object(self):
        return ManufacturerProfile.objects.select_related("organisation").get(
            organisation_id=self.request.user.organisation_id
        )


class ProductRegisterView(generics.CreateAPIView):
    """Register a medicine product against the manufacturer's organisation (Phase 8)."""

    serializer_class = ProductRegisterSerializer
    permission_classes = [IsAuthenticated, IsManufacturerStaff]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["organisation_id"] = self.request.user.organisation_id
        return ctx


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
        return api_response(
            data={
                "batch": ProductBatchSerializer(batch).data,
                "serials_issued": 0,
                "serial_range": [batch.serial_range_start, batch.serial_range_end],
            },
            message="National batch created — submit for regulator approval before generating serials",
            status_code=status.HTTP_201_CREATED,
        )


class BatchSubmitForApprovalView(APIView):
    permission_classes = [IsAuthenticated, IsManufacturerStaff]

    def post(self, request, pk):
        batch = ProductBatch.objects.get(pk=pk)
        site_org = batch.manufacturing_site.manufacturer.organisation_id if batch.manufacturing_site_id else None
        if str(site_org) != str(request.user.organisation_id):
            return api_response(message="Forbidden", status_code=403)
        submit_batch_for_regulator_review(batch=batch, actor=request.user)
        return api_response(data=ProductBatchSerializer(batch).data, message="Batch submitted for regulator review")


class BatchGenerateSerialsView(APIView):
    permission_classes = [IsAuthenticated, IsManufacturerStaff]

    def post(self, request, pk):
        ser = GenerateBatchSerialsSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        batch = ProductBatch.objects.get(pk=pk)
        site_org = batch.manufacturing_site.manufacturer.organisation_id if batch.manufacturing_site_id else None
        if str(site_org) != str(request.user.organisation_id):
            return api_response(message="Forbidden", status_code=403)
        try:
            serials = issue_batch_serials(batch=batch, count=ser.validated_data["count"], actor=request.user)
        except Exception as exc:
            return api_response(message=str(exc), status_code=400)
        return api_response(
            data={
                "batch": ProductBatchSerializer(batch).data,
                "issued": len(serials),
                "first_serial": serials[0].serial_number if serials else None,
                "last_serial": serials[-1].serial_number if serials else None,
            },
            message="Serials issued",
            status_code=status.HTTP_201_CREATED,
        )


class RecallNoticeCreateView(generics.CreateAPIView):
    serializer_class = RecallNoticeSerializer
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
