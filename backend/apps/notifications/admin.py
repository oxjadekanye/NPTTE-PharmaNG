from django.contrib import admin

from apps.notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "recipient", "channel", "is_read", "created_at")
    list_filter = ("channel", "is_read", "status")
    search_fields = ("title", "body")
