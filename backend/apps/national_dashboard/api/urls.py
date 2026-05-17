from django.urls import path

from apps.national_dashboard.api.views import NationalOverviewDashboardView

urlpatterns = [
    path("overview/", NationalOverviewDashboardView.as_view(), name="dashboard-overview"),
]
