from litestar import Router

from app.domain.tasks import Task

from . import tasks

__all__ = ["create_router"]


def create_router() -> Router:
    return Router(path="/v1", route_handlers=[tasks.ApiController], signature_namespace={"Task": Task})
