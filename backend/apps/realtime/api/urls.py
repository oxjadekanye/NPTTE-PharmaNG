from django.urls import path

from apps.realtime.api.views import RealtimeStreamView

urlpatterns = [
    path("stream/", RealtimeStreamView.as_view(), name="realtime-stream"),
]
