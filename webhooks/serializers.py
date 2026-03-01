from rest_framework import serializers

from .models import WebhookEndpoint


class WebhookEndpointSerializer(serializers.ModelSerializer):
    sid = serializers.UUIDField(read_only=True)

    class Meta:
        model = WebhookEndpoint
        fields = [
            "sid",
            "url",
            "events",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["sid", "created_at", "updated_at"]
