from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.permissions import IsRegulatorUser
from apps.international.api.serializers import (
    BorderVerificationLogSerializer,
    ExportManifestSerializer,
    ImportManifestSerializer,
)
from apps.international.models import BorderVerificationLog, ExportManifest, ImportManifest


class ImportManifestListView(generics.ListAPIView):
    serializer_class = ImportManifestSerializer
    permission_classes = [IsAuthenticated, IsRegulatorUser]
    queryset = ImportManifest.objects.select_related("importer").order_by("-declared_at")[:100]


class ExportManifestListView(generics.ListAPIView):
    serializer_class = ExportManifestSerializer
    permission_classes = [IsAuthenticated, IsRegulatorUser]
    queryset = ExportManifest.objects.select_related("exporter").order_by("-declared_at")[:100]


class BorderVerificationLogListView(generics.ListAPIView):
    serializer_class = BorderVerificationLogSerializer
    permission_classes = [IsAuthenticated, IsRegulatorUser]
    queryset = BorderVerificationLog.objects.order_by("-verified_at")[:200]


class ValidateImportManifestView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def post(self, request, pk):
        from apps.international.services import validate_import_manifest

        manifest = ImportManifest.objects.get(pk=pk)
        result = validate_import_manifest(manifest=manifest)
        return api_response(data=result, message="Import manifest validated")
