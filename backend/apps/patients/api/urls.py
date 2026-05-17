from django.urls import path

from apps.patients.api.views import (
    MedicationCompareView,
    MedicationReminderListCreateView,
    MedicationSearchDetailView,
    MedicationSearchHistoryView,
    MedicationSearchView,
    NearbyPharmaciesView,
    PatientProfileView,
    ProductCatalogSearchView,
    SavedMedicationDetailView,
    SavedMedicationListCreateView,
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
    path("saved-medications/", SavedMedicationListCreateView.as_view(), name="saved-medications"),
    path(
        "saved-medications/<uuid:pk>/",
        SavedMedicationDetailView.as_view(),
        name="saved-medication-detail",
    ),
    path("refill-reminders/", MedicationReminderListCreateView.as_view(), name="refill-reminders"),
    path("medication-compare/", MedicationCompareView.as_view(), name="medication-compare"),
]
