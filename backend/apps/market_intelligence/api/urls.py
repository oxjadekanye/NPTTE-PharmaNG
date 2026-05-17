from django.urls import path

from apps.market_intelligence.api.views import MarketPressureView

urlpatterns = [
    path("pressure/", MarketPressureView.as_view(), name="market-pressure"),
]
