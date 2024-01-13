from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import CustomUser


class CustomUserAdmin(BaseUserAdmin):
    fieldsets = (
        ("UUID", {"fields": ("user_id",)}),
        (None, {"fields": ("email", "password")}),
        (
            "Personal Info",
            {
                "fields": (
                    "name",
                    "telephone",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_admin",
                    "is_staff",
                    "is_superuser",
                    "is_group_leader",
                    "is_deleted",
                )
            },
        ),
    )

    list_display = (
        "name",
        "email",
        "is_staff",
        "is_superuser",
        "is_admin",
        "is_deleted",
    )

    list_filter = (
        "is_staff",
        "is_admin",
        "is_deleted",
        "is_group_leader",
        "is_superuser",
    )

    search_fields = ("name", "email")

    ordering = ("name", "email")

    def save_model(self, request, obj, form, change):
        if obj.id is not None:
            obj.id = str(obj.id)

        super().save_model(request, obj, form, change)


admin.site.register(CustomUser, CustomUserAdmin)
