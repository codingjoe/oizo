from rest_framework import serializers

from .models import PhoneNumber


class PhoneNumberSerializer(serializers.ModelSerializer):
    sid = serializers.UUIDField(read_only=True)

    class Meta:
        model = PhoneNumber
        fields = [
            "sid",
            "phone_number",
            "friendly_name",
            "iso_country",
            "number_type",
            "status",
            "voice_url",
            "voice_method",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["sid", "created_at", "updated_at"]
