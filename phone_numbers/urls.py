from rest_framework.routers import DefaultRouter

from .views import PhoneNumberViewSet

router = DefaultRouter()
router.register(r"numbers", PhoneNumberViewSet, basename="phonenumber")

urlpatterns = router.urls
