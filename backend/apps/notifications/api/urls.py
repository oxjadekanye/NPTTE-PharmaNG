from django.urls import path

from apps.notifications.api.views import NotificationBroadcastView, NotificationCenterView

urlpatterns = [
    path("center/", NotificationCenterView.as_view(), name="notifications-center"),
    path("broadcast/", NotificationBroadcastView.as_view(), name="notifications-broadcast"),
]
