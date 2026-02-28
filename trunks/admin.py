from django.contrib import admin

from .models import Trunk


@admin.register(Trunk)
class TrunkAdmin(admin.ModelAdmin):
    list_display = ["sid", "friendly_name", "domain_name", "secure", "created_at"]
    list_filter = ["secure", "recording_enabled"]
    search_fields = ["sid", "friendly_name", "domain_name"]
    readonly_fields = ["sid", "created_at", "updated_at"]
