from django.contrib import admin

from .models import PhoneNumber


@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = [
        "phone_number",
        "friendly_name",
        "iso_country",
        "number_type",
        "status",
    ]
    list_filter = ["iso_country", "number_type", "status"]
    search_fields = ["phone_number", "friendly_name", "sipgate_id"]
    readonly_fields = ["sid", "created_at", "updated_at"]
