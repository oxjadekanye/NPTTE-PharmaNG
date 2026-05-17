from django.urls import path

from apps.events.api.views import EventReplayView

urlpatterns = [
    path("replay/", EventReplayView.as_view(), name="events-replay"),
]
