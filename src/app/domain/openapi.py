from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.controller import OpenAPIController
from litestar.openapi.spec import Contact

from app.domain.security import auth
from app.lib import settings

__all__ = ["LatestSwaggerController"]


class LatestSwaggerController(OpenAPIController):
    swagger_css_url = f"{settings.openapi.LOCAL_CDN}/swagger-dark-ui.css"
    swagger_ui_bundle_js_url = f"{settings.openapi.LOCAL_CDN}/swagger-ui-bundle.js"
    swagger_ui_standalone_preset_js_url = f"{settings.openapi.LOCAL_CDN}/swagger-ui-standalone-preset.min.js"


config = OpenAPIConfig(
    openapi_controller=LatestSwaggerController,
    title=settings.openapi.TITLE or settings.app.NAME,
    version=settings.openapi.VERSION,
    contact=Contact(name=settings.openapi.CONTACT_NAME, email=settings.openapi.CONTACT_EMAIL),
    components=[auth.openapi_components],
    security=[auth.security_requirement],
    use_handler_docstrings=True,
    enabled_endpoints={"swagger"},
    root_schema_site="swagger",
)
"""OpenAPI config for app.  See OpenAPISettings for configuration.

Defaults to 'elements' for the documentation.  It has an interactive 3.1
compliant web app and Swagger does not yet support 3.1
"""
