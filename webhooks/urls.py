from rest_framework.routers import DefaultRouter

from .views import WebhookEndpointViewSet

router = DefaultRouter()
router.register(r"webhooks", WebhookEndpointViewSet, basename="webhook")

urlpatterns = router.urls
