from django.contrib import admin

from apps.international.models import BorderVerificationLog, ExportManifest, ImportManifest


@admin.register(ImportManifest)
class ImportManifestAdmin(admin.ModelAdmin):
    list_display = ("manifest_number", "importer", "origin_country", "declared_at")
    search_fields = ("manifest_number",)


@admin.register(ExportManifest)
class ExportManifestAdmin(admin.ModelAdmin):
    list_display = ("manifest_number", "exporter", "destination_country", "declared_at")


@admin.register(BorderVerificationLog)
class BorderVerificationLogAdmin(admin.ModelAdmin):
    list_display = ("border_point", "verification_outcome", "verified_at")
