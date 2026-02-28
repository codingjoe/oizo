from django.contrib import admin

from .models import APIKey


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "is_active", "created_at", "last_used_at"]
    list_filter = ["is_active"]
    search_fields = ["name", "user__username"]
    readonly_fields = ["key", "created_at", "last_used_at"]
