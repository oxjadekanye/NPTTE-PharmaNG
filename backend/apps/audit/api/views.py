from django_filters import rest_framework as filters
from rest_framework import generics

from apps.audit.api.serializers import AuditLogSerializer
from apps.audit.models import AuditLog
from apps.core.permissions import IsRegulatorUser


class AuditLogFilter(filters.FilterSet):
    action = filters.CharFilter(lookup_expr="icontains")
    entity_type = filters.CharFilter()
    entity_id = filters.UUIDFilter()
    actor = filters.UUIDFilter()
    created_at_after = filters.IsoDateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_at_before = filters.IsoDateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = AuditLog
        fields = ["action", "entity_type", "entity_id", "actor"]


class AuditLogListView(generics.ListAPIView):
    """Forensic audit log access for regulators and auditors."""

    serializer_class = AuditLogSerializer
    permission_classes = [IsRegulatorUser]
    filterset_class = AuditLogFilter
    queryset = AuditLog.objects.select_related("actor").order_by("-created_at")
