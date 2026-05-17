from django.contrib import admin

from apps.verification.models import VerificationEvent


@admin.register(VerificationEvent)
class VerificationEventAdmin(admin.ModelAdmin):
    list_display = ("product_serial", "channel", "is_authentic", "created_at")
    list_filter = ("channel", "is_authentic")
