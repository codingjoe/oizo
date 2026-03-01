from django.apps import AppConfig


class AuthTokensConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "auth_tokens"
    verbose_name = "API Keys"

    def ready(self):
        import auth_tokens.openapi  # noqa: F401 – registers OpenAPI extension
