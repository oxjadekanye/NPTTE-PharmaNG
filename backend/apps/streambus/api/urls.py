from django.urls import path

from apps.streambus.api.views import (
    CommandCenterLiveView,
    ScopedEventReplayView,
    DeferredTaskQueueView,
    EscalationListView,
    EventAcknowledgeView,
    EventLifecycleView,
    EventPublishView,
    EventReplayView,
    TelemetryView,
)

urlpatterns = [
    path("publish/", EventPublishView.as_view(), name="streambus-publish"),
    path("replay/", EventReplayView.as_view(), name="streambus-replay"),
    path("scoped-replay/", ScopedEventReplayView.as_view(), name="streambus-scoped-replay"),
    path("acknowledge/<str:event_id>/", EventAcknowledgeView.as_view(), name="streambus-ack"),
    path("telemetry/", TelemetryView.as_view(), name="streambus-telemetry"),
    path("escalations/", EscalationListView.as_view(), name="streambus-escalations"),
    path("lifecycle/", EventLifecycleView.as_view(), name="streambus-lifecycle"),
    path("deferred-queue/", DeferredTaskQueueView.as_view(), name="streambus-deferred"),
    path("command-center/live/", CommandCenterLiveView.as_view(), name="streambus-command-live"),
]
