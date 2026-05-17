from django.contrib import admin

from apps.emergency.models import EmergencyMedicineWatchlist


@admin.register(EmergencyMedicineWatchlist)
class EmergencyMedicineWatchlistAdmin(admin.ModelAdmin):
    list_display = ("product", "category", "minimum_national_stock", "is_active_watch", "epidemic_code")
    list_filter = ("category", "is_active_watch")
