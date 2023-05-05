from litestar import Router

from app.domain.backlogs import Backlog
from app.domain.projects import Project
from app.domain.users import User

from . import backlogs, projects, users

__all__ = ["create_router"]


def create_router() -> Router:
    return Router(
        path="/v1",
        route_handlers=[
            backlogs.ApiController,
            users.ApiController,
            projects.ApiController,
        ],
        signature_namespace={"Task": Backlog, "User": User, "Project": Project},
    )
