from django.urls import path

from apps.prescriptions.api.views import (
    PrescriptionDetailView,
    PrescriptionDispenseView,
    PrescriptionListCreateView,
    PrescriptionRiskView,
    RefillAuthorizationView,
)

urlpatterns = [
    path("", PrescriptionListCreateView.as_view(), name="prescriptions-list"),
    path("<uuid:pk>/", PrescriptionDetailView.as_view(), name="prescriptions-detail"),
    path("<uuid:pk>/risk/", PrescriptionRiskView.as_view(), name="prescriptions-risk"),
    path("<uuid:pk>/dispense/", PrescriptionDispenseView.as_view(), name="prescriptions-dispense"),
    path("<uuid:prescription_id>/refill/", RefillAuthorizationView.as_view(), name="prescriptions-refill"),
]
