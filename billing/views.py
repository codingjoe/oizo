from rest_framework import generics, permissions

from auth_tokens.models import APIKey

from .models import UsageRecord, Wallet
from .serializers import UsageRecordSerializer, WalletSerializer


class UsageRecordListView(generics.ListAPIView):
    """
    List usage records for the authenticated client.

    Supports filtering by `resource_type` and `call_sid` query parameters.
    """

    serializer_class = UsageRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        api_keys = APIKey.objects.filter(user=self.request.user)
        qs = UsageRecord.objects.filter(api_key__in=api_keys)
        resource_type = self.request.query_params.get("resource_type")
        if resource_type:
            qs = qs.filter(resource_type=resource_type)
        call_sid = self.request.query_params.get("call_sid")
        if call_sid:
            qs = qs.filter(call_sid=call_sid)
        return qs


class WalletView(generics.RetrieveAPIView):
    """
    Retrieve the current wallet balance for the authenticated client.
    """

    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        api_key = self.request.auth
        if not isinstance(api_key, APIKey):
            # Fallback for session auth (e.g. browsable API)
            api_key = APIKey.objects.filter(user=self.request.user).first()
        if api_key is None:
            return Wallet(balance=0)
        wallet, _ = Wallet.objects.get_or_create(api_key=api_key)
        return wallet
