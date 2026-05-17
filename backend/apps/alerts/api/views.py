from django_filters import rest_framework as filters
from rest_framework import generics

from apps.alerts.api.serializers import NationalAlertSerializer
from apps.alerts.models import NationalAlert
from apps.core.permissions import IsRegulatorUser


class NationalAlertFilter(filters.FilterSet):
    alert_type = filters.CharFilter()
    severity = filters.CharFilter()
    state = filters.CharFilter()
    risk_level = filters.CharFilter()

    class Meta:
        model = NationalAlert
        fields = ["alert_type", "severity", "state", "risk_level"]


class NationalAlertListView(generics.ListAPIView):
    serializer_class = NationalAlertSerializer
    permission_classes = [IsRegulatorUser]
    filterset_class = NationalAlertFilter
    queryset = NationalAlert.objects.select_related("organisation", "product").order_by(
        "-created_at"
    )
