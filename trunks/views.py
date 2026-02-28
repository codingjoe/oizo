from rest_framework import viewsets

from .models import Trunk
from .serializers import TrunkSerializer


class TrunkViewSet(viewsets.ModelViewSet):
    """
    Manage SIP trunks.

    SIP trunks connect the platform to the public switched telephone network (PSTN)
    via carrier-provided SIP endpoints.
    """

    queryset = Trunk.objects.all()
    serializer_class = TrunkSerializer
    lookup_field = "sid"
