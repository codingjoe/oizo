"""
URL configuration for the Oizo Voice API.

API documentation (Swagger UI) is served at the root URL.
All REST endpoints live under /v1/.
"""

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from health_check.views import HealthCheckView

urlpatterns = [
    # OpenAPI schema + interactive documentation at the root
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("", SpectacularSwaggerView.as_view(url_name="schema"), name="home"),
    # Admin
    path("admin/", admin.site.urls),
    # Health check
    path("health/", HealthCheckView.as_view(
        checks=[
                "health_check.contrib.psutil.Disk",
                "health_check.contrib.psutil.Memory",
        ]
    ), name="health"),
    path("api/", include([
        path("v1/", include([
            path("", include("calls.urls")),
            path("", include("phone_numbers.urls")),
            path("", include("webhooks.urls")),
            path("", include("billing.urls")),

        ])),
    ])),
]
