from django.urls import path

from apps.international.api.views import (
    BorderVerificationLogListView,
    ExportManifestListView,
    ImportManifestListView,
    ValidateImportManifestView,
)

urlpatterns = [
    path("imports/", ImportManifestListView.as_view(), name="international-imports"),
    path("imports/<uuid:pk>/validate/", ValidateImportManifestView.as_view(), name="international-validate-import"),
    path("exports/", ExportManifestListView.as_view(), name="international-exports"),
    path("border-logs/", BorderVerificationLogListView.as_view(), name="international-border-logs"),
]
