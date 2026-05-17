from django.urls import path

from apps.verification.api.views import (
    VerificationHistoryView,
    VerificationScanLogListView,
    VerifyMedicationView,
)

urlpatterns = [
    path("authenticate/", VerifyMedicationView.as_view(), name="verify-medication"),
    path("history/", VerificationHistoryView.as_view(), name="verify-history"),
    path("scan-logs/", VerificationScanLogListView.as_view(), name="verify-scan-logs"),
]
