from django.urls import path

from apps.emergency.api.views import EmergencyWatchlistView

urlpatterns = [
    path("watchlist/", EmergencyWatchlistView.as_view(), name="emergency-watchlist"),
]
