from django.urls import path

from apps.patients.api.views import (
    MedicationSearchDetailView,
    MedicationSearchHistoryView,
    MedicationSearchView,
    NearbyPharmaciesView,
    PatientProfileView,
    ProductCatalogSearchView,
)

urlpatterns = [
    path("profile/", PatientProfileView.as_view(), name="patient-profile"),
    path("products/search/", ProductCatalogSearchView.as_view(), name="product-catalog-search"),
    path("medication-search/", MedicationSearchView.as_view(), name="medication-search"),
    path("nearby-pharmacies/", NearbyPharmaciesView.as_view(), name="nearby-pharmacies"),
    path("search-history/", MedicationSearchHistoryView.as_view(), name="search-history"),
    path(
        "search-history/<uuid:pk>/",
        MedicationSearchDetailView.as_view(),
        name="search-history-detail",
    ),
]
