from django.urls import path

from apps.events.api.views import EventReplayView, NationalOperationsSummaryView

urlpatterns = [
    path("replay/", EventReplayView.as_view(), name="events-replay"),
    path("national-summary/", NationalOperationsSummaryView.as_view(), name="events-national-summary"),
]
