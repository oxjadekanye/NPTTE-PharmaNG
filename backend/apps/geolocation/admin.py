from django.contrib import admin

from apps.geolocation.models import GeolocationEvent


@admin.register(GeolocationEvent)
class GeolocationEventAdmin(admin.ModelAdmin):
    list_display = ("event_type", "organisation", "latitude", "longitude", "created_at")
    list_filter = ("event_type",)
