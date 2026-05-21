from django.urls import path

from apps.alerts.api.alert_center_views import NationalAlertCenterView
from apps.alerts.api.views import NationalAlertListView

urlpatterns = [
    path("", NationalAlertListView.as_view(), name="national-alerts"),
    path("center/", NationalAlertCenterView.as_view(), name="national-alert-center"),
]
