import logging

from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from sipgate import client as sipgate

from .models import Call
from .serializers import CallCreateSerializer, CallSerializer

logger = logging.getLogger(__name__)


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

    **Create an outbound call** (`POST /v1/calls/`):
    Initiates a call via the Sipgate SIP trunk. The call transitions through
    `init → validate → route → ringing → answered → completed` states.

    **Cancel an active call** (`DELETE /v1/calls/{sid}/`):
    Hangs up calls in `ringing` or `answered` state.
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
        call = serializer.save(status=Call.Status.INIT)

        # Advance through the state machine: INIT → VALIDATE → ROUTE → RINGING
        call.status = Call.Status.VALIDATE
        call.save(update_fields=["status"])

        # TODO: invoke Fraud/Policy agent here

        call.status = Call.Status.ROUTE
        call.save(update_fields=["status"])

        # Initiate call via Sipgate
        try:
            result = sipgate.initiate_call(
                caller=call.from_number,
                callee=call.to_number,
            )
            call.sipgate_session_id = result.get("sessionId", "")
            call.status = Call.Status.RINGING
        except Exception as exc:  # noqa: BLE001
            logger.error("Sipgate call initiation failed for %s: %s", call.sid, exc)
            call.status = Call.Status.FAILED
        call.save(update_fields=["status", "sipgate_session_id"])

        return Response(CallSerializer(call).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """Hang up an active call."""
        call = self.get_object()
        if call.is_terminal:
            return Response(
                {"detail": "Call is already in a terminal state."},
                status=status.HTTP_409_CONFLICT,
            )
        if call.sipgate_session_id:
            try:
                sipgate.hangup_call(call.sipgate_session_id)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Sipgate hangup failed for %s: %s", call.sid, exc)
        call.status = Call.Status.CANCELED
        call.save(update_fields=["status"])
        return Response(CallSerializer(call).data)
