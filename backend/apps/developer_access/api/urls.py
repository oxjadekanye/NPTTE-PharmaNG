from django.urls import path

from apps.developer_access.api.views import DeveloperKeysView, DeveloperPortalOverviewView

urlpatterns = [
    path("overview/", DeveloperPortalOverviewView.as_view(), name="developer-overview"),
    path("keys/", DeveloperKeysView.as_view(), name="developer-keys"),
]
