from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsDistributorStaff
from apps.core.roles import is_regulator_user
from apps.distributors.api.serializers import DistributorProfileSerializer, WarehouseSerializer
from apps.distributors.models import DistributorProfile, Warehouse


class DistributorProfileView(generics.RetrieveAPIView):
    serializer_class = DistributorProfileSerializer
    permission_classes = [IsAuthenticated, IsDistributorStaff]

    def get_object(self):
        return DistributorProfile.objects.select_related("organisation").get(
            organisation_id=self.request.user.organisation_id
        )


class WarehouseListCreateView(generics.ListCreateAPIView):
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ("GET",):
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsDistributorStaff()]

    def get_queryset(self):
        user = self.request.user
        qs = Warehouse.objects.filter(is_active=True).select_related("organisation")
        if is_regulator_user(user):
            org_id = self.request.query_params.get("organisation_id")
            if org_id:
                return qs.filter(organisation_id=org_id)
            return qs
        if user.organisation_id:
            return qs.filter(organisation_id=user.organisation_id)
        return qs.none()

    def perform_create(self, serializer):
        profile = DistributorProfile.objects.get(organisation_id=self.request.user.organisation_id)
        serializer.save(
            organisation_id=self.request.user.organisation_id,
            distributor=profile,
            created_by=self.request.user,
        )


class WarehouseDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated, IsDistributorStaff]

    def get_queryset(self):
        return Warehouse.objects.filter(organisation_id=self.request.user.organisation_id)
