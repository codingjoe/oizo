from rest_framework import viewsets

from .models import PhoneNumber
from .serializers import PhoneNumberSerializer


class PhoneNumberViewSet(viewsets.ModelViewSet):
    """
    Manage provisioned phone numbers.

    Numbers can receive inbound calls routed to a `voice_url` webhook,
    or be used as the caller ID for outbound calls.
    """

    queryset = PhoneNumber.objects.all()
    serializer_class = PhoneNumberSerializer
    lookup_field = "sid"
