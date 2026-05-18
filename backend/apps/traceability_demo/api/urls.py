from django.urls import path

from apps.traceability_demo.api.views import TraceabilityStoryView

urlpatterns = [
    path("traceability-story/", TraceabilityStoryView.as_view(), name="demo-traceability-story"),
]
