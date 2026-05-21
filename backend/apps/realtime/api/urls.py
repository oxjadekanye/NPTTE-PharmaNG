from django.urls import path

from apps.realtime.api.operational_feed_views import OperationalFeedPollingView, OperationalPrefetchView
from apps.realtime.api.views import RealtimeStreamView, RealtimeWebSocketInfoView

urlpatterns = [
    path("stream/", RealtimeStreamView.as_view(), name="realtime-stream"),
    path("transport/", RealtimeWebSocketInfoView.as_view(), name="realtime-transport-info"),
    path("operational-feed/", OperationalFeedPollingView.as_view(), name="realtime-operational-feed"),
    path("prefetch/", OperationalPrefetchView.as_view(), name="realtime-prefetch"),
]
