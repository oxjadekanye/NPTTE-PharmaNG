from django.urls import path

from apps.alerts.api.views import NationalAlertListView

urlpatterns = [
    path("", NationalAlertListView.as_view(), name="national-alerts"),
]
