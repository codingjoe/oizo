from django.contrib import admin

from .models import WebhookDelivery, WebhookEndpoint


@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(admin.ModelAdmin):
    list_display = ["url", "user", "is_active", "created_at"]
    list_filter = ["is_active"]
    readonly_fields = ["sid", "created_at", "updated_at"]


@admin.register(WebhookDelivery)
class WebhookDeliveryAdmin(admin.ModelAdmin):
    list_display = ["event_type", "endpoint", "status", "attempt_count", "created_at"]
    list_filter = ["status", "event_type"]
    readonly_fields = ["sid", "created_at", "updated_at"]
