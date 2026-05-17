from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.accounts.models import Role, User


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active", "created_at")
    search_fields = ("name", "code")
    list_filter = ("is_active",)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "role", "organisation", "is_regulator", "status", "is_active")
    list_filter = ("is_regulator", "status", "is_staff", "is_active", "role")
    search_fields = ("username", "email", "phone_number", "national_id_number")
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "NPTTE profile",
            {
                "fields": (
                    "phone_number",
                    "national_id_number",
                    "role",
                    "organisation",
                    "is_regulator",
                    "status",
                    "metadata",
                ),
            },
        ),
    )
