from rest_framework import serializers

from apps.international.models import BorderVerificationLog, ExportManifest, ImportManifest


class ImportManifestSerializer(serializers.ModelSerializer):
    importer_name = serializers.CharField(source="importer.legal_name", read_only=True)

    class Meta:
        model = ImportManifest
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "created_by")


class ExportManifestSerializer(serializers.ModelSerializer):
    exporter_name = serializers.CharField(source="exporter.legal_name", read_only=True)

    class Meta:
        model = ExportManifest
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "created_by")


class BorderVerificationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = BorderVerificationLog
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "created_by")
