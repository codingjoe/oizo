from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from .models import Call
from .serializers import CallCreateSerializer, CallSerializer


class CallViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    Manage voice calls.

    Supports creating outbound calls, listing calls, retrieving call details,
    updating call status (e.g., to cancel a queued call), and ending active calls.
    """

    queryset = Call.objects.all()
    lookup_field = "sid"

    def get_serializer_class(self):
        if self.action == "create":
            return CallCreateSerializer
        return CallSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        call = serializer.save()
        return Response(CallSerializer(call).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """End an active call by setting its status to canceled."""
        call = self.get_object()
        if call.status in (
            Call.Status.QUEUED,
            Call.Status.RINGING,
            Call.Status.IN_PROGRESS,
        ):
            call.status = Call.Status.CANCELED
            call.save(update_fields=["status"])
            return Response(CallSerializer(call).data)
        return Response(
            {"detail": "Call is already completed."},
            status=status.HTTP_409_CONFLICT,
        )
