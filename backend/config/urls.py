"""
Root URL configuration for NPTTE backend.

API routers will be mounted here as modules mature beyond Phase 1.
"""
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
]
