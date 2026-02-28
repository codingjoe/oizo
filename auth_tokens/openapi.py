"""
OpenAPI extensions for drf-spectacular.
"""

from drf_spectacular.extensions import OpenApiAuthenticationExtension


class APIKeyAuthenticationExtension(OpenApiAuthenticationExtension):
    """Describe our bearer-token API key scheme in the OpenAPI schema."""

    target_class = "auth_tokens.authentication.APIKeyAuthentication"
    name = "ApiKeyAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "API Key",
            "description": "Authenticate using your Oizo API key: `Authorization: Bearer <key>`",
        }
