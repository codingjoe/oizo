from django.contrib import admin

from .models import Call


@admin.register(Call)
class CallAdmin(admin.ModelAdmin):
    list_display = [
        "sid",
        "status",
        "direction",
        "from_number",
        "to_number",
        "created_at",
    ]
    list_filter = ["status", "direction"]
    search_fields = ["sid", "from_number", "to_number"]
    readonly_fields = ["sid", "created_at", "updated_at"]
