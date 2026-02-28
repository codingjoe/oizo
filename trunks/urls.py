from rest_framework.routers import DefaultRouter

from .views import TrunkViewSet

router = DefaultRouter()
router.register(r"trunks", TrunkViewSet, basename="trunk")

urlpatterns = router.urls
