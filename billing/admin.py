from django.contrib import admin

from .models import UsageRecord, Wallet


@admin.register(UsageRecord)
class UsageRecordAdmin(admin.ModelAdmin):
    list_display = [
        "resource_type",
        "call_sid",
        "duration_seconds",
        "amount",
        "recorded_at",
    ]
    list_filter = ["resource_type"]
    readonly_fields = ["sid", "recorded_at"]


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ["api_key", "balance", "updated_at"]
    readonly_fields = ["updated_at"]
