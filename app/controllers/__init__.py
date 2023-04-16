from litestar import Router

from app.domain.projects import Project
from app.domain.tasks import Task
from app.domain.users import User

from . import projects, tasks, users

__all__ = ["create_router"]


def create_router() -> Router:
    return Router(
        path="/v1",
        route_handlers=[tasks.ApiController, users.ApiController, projects.ApiController],
        signature_namespace={"Task": Task, "User": User, "Project": Project},
    )
