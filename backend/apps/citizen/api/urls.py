from django.urls import path

from apps.citizen.api.phase11_views import (
    CitizenMedicationSearchView,
    CitizenPublicNoticesView,
    CitizenSafetyGuidanceView,
    CitizenVerificationHistoryView,
)
from apps.citizen.api.views import PublicRecallsView, PublicVerifyView, ReportCounterfeitView, TrustedPharmaciesView

urlpatterns = [
    path("verify/", PublicVerifyView.as_view(), name="public-verify"),
    path("report-counterfeit/", ReportCounterfeitView.as_view(), name="public-report-counterfeit"),
    path("recalls/", PublicRecallsView.as_view(), name="public-recalls"),
    path("trusted-pharmacies/", TrustedPharmaciesView.as_view(), name="public-trusted-pharmacies"),
    path("verification-history/", CitizenVerificationHistoryView.as_view(), name="citizen-verification-history"),
    path("medication-search/", CitizenMedicationSearchView.as_view(), name="citizen-medication-search"),
    path("safety-guidance/", CitizenSafetyGuidanceView.as_view(), name="citizen-safety-guidance"),
    path("public-notices/", CitizenPublicNoticesView.as_view(), name="citizen-public-notices"),
]
