from rest_framework import serializers

from .models import Call


class CallSerializer(serializers.ModelSerializer):
    sid = serializers.UUIDField(read_only=True)

    class Meta:
        model = Call
        fields = [
            "sid",
            "status",
            "direction",
            "from_number",
            "to_number",
            "status_callback",
            "start_time",
            "end_time",
            "duration",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "sid",
            "status",
            "start_time",
            "end_time",
            "duration",
            "created_at",
            "updated_at",
        ]


class CallCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Call
        fields = ["from_number", "to_number", "status_callback"]
