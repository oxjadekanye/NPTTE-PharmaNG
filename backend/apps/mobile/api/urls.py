from django.urls import path

from apps.mobile.api.views import DeviceListView, DeviceRegisterView

urlpatterns = [
    path("devices/register/", DeviceRegisterView.as_view(), name="mobile-device-register"),
    path("devices/", DeviceListView.as_view(), name="mobile-device-list"),
]
