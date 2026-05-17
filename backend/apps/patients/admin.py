from django.contrib import admin

from apps.patients.models import MedicationSearchRequest, PatientProfile


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ("preferred_name", "phone_number", "consent_to_location_search", "is_active")
    list_filter = ("consent_to_location_search", "status", "is_active")


@admin.register(MedicationSearchRequest)
class MedicationSearchRequestAdmin(admin.ModelAdmin):
    list_display = ("product", "radius_miles", "search_status", "result_count", "created_at")
    list_filter = ("search_status",)
    search_fields = ("search_term", "product__name")
