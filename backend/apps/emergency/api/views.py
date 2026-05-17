from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsRegulatorUser
from apps.emergency.api.serializers import EmergencyWatchlistSerializer
from apps.emergency.models import EmergencyMedicineWatchlist


class EmergencyWatchlistView(generics.ListCreateAPIView):
    serializer_class = EmergencyWatchlistSerializer
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get_queryset(self):
        qs = EmergencyMedicineWatchlist.objects.filter(is_active=True).select_related("product")
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category=category)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
