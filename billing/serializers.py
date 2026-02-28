from rest_framework import serializers

from .models import UsageRecord, Wallet


class UsageRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsageRecord
        fields = [
            "sid",
            "resource_type",
            "call_sid",
            "duration_seconds",
            "amount",
            "recorded_at",
        ]
        read_only_fields = fields


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ["balance", "updated_at"]
        read_only_fields = fields
