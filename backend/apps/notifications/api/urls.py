from django.urls import path

from apps.notifications.api.views import (
    NotificationBroadcastView,
    NotificationCenterView,
    NotificationUnreadView,
)

urlpatterns = [
    path("center/", NotificationCenterView.as_view(), name="notifications-center"),
    path("unread/", NotificationUnreadView.as_view(), name="notifications-unread"),
    path("broadcast/", NotificationBroadcastView.as_view(), name="notifications-broadcast"),
]
