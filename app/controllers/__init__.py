from litestar import Router

from app.domain.backlogs import Backlog
from app.domain.projects import Project

from . import backlogs, projects

__all__ = ["create_router"]


def create_router() -> Router:
    return Router(
        path="/v1",
        route_handlers=[
            projects.ApiController,
            backlogs.ApiController,
        ],
        signature_namespace={"Project": Project, "BL": Backlog},
    )
