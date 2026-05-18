from django.urls import path

from apps.realtime.api.views import RealtimeStreamView, RealtimeWebSocketInfoView

urlpatterns = [
    path("stream/", RealtimeStreamView.as_view(), name="realtime-stream"),
    path("transport/", RealtimeWebSocketInfoView.as_view(), name="realtime-transport-info"),
]
