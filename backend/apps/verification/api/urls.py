from django.urls import path

from apps.verification.api.views import VerificationHistoryView, VerifyMedicationView

urlpatterns = [
    path("authenticate/", VerifyMedicationView.as_view(), name="verify-medication"),
    path("history/", VerificationHistoryView.as_view(), name="verify-history"),
]
