from rest_framework import permissions, viewsets

from .models import WebhookEndpoint
from .serializers import WebhookEndpointSerializer


class WebhookEndpointViewSet(viewsets.ModelViewSet):
    """
    Manage webhook endpoints.

    Register HTTPS URLs to receive real-time call-event notifications.
    Subscribed events can be filtered per endpoint.
    """

    serializer_class = WebhookEndpointSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "sid"
    queryset = WebhookEndpoint.objects.none()  # overridden in get_queryset

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return WebhookEndpoint.objects.none()
        return WebhookEndpoint.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
