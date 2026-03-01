from django.utils import timezone
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import APIKey


class APIKeyAuthentication(BaseAuthentication):
    """
    Authenticate requests using the ``Authorization: Bearer <key>`` header.
    """

    keyword = "Bearer"

    def authenticate(self, request):
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth.startswith(self.keyword + " "):
            return None
        raw_key = auth[len(self.keyword) + 1 :].strip()
        try:
            api_key = APIKey.objects.select_related("user").get(
                key=raw_key, is_active=True
            )
        except APIKey.DoesNotExist:
            raise AuthenticationFailed("Invalid or inactive API key.")
        api_key.last_used_at = timezone.now()
        api_key.save(update_fields=["last_used_at"])
        return (api_key.user, api_key)

    def authenticate_header(self, request):
        return self.keyword
