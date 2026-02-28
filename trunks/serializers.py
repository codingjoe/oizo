from rest_framework import serializers

from .models import Trunk


class TrunkSerializer(serializers.ModelSerializer):
    sid = serializers.UUIDField(read_only=True)

    class Meta:
        model = Trunk
        fields = [
            "sid",
            "friendly_name",
            "domain_name",
            "disaster_recovery_url",
            "disaster_recovery_method",
            "recording_enabled",
            "secure",
            "cnam_lookup_enabled",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["sid", "created_at", "updated_at"]
