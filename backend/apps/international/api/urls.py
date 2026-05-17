from django.urls import path

from apps.international.api.views import (
    BorderVerificationLogListView,
    ExportManifestListView,
    ImportManifestListView,
)

urlpatterns = [
    path("imports/", ImportManifestListView.as_view(), name="international-imports"),
    path("exports/", ExportManifestListView.as_view(), name="international-exports"),
    path("border-logs/", BorderVerificationLogListView.as_view(), name="international-border-logs"),
]
