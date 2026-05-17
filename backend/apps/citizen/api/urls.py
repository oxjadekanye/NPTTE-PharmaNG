from django.urls import path

from apps.citizen.api.views import PublicRecallsView, PublicVerifyView, ReportCounterfeitView, TrustedPharmaciesView

urlpatterns = [
    path("verify/", PublicVerifyView.as_view(), name="public-verify"),
    path("report-counterfeit/", ReportCounterfeitView.as_view(), name="public-report-counterfeit"),
    path("recalls/", PublicRecallsView.as_view(), name="public-recalls"),
    path("trusted-pharmacies/", TrustedPharmaciesView.as_view(), name="public-trusted-pharmacies"),
]
