from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.dto import DTOConfig

from typing import Annotated
from app.db.models import Project


__all__ = ["ReadDTO", "WriteDTO"]

WriteDTO = SQLAlchemyDTO[
    Annotated[
        Project,
        DTOConfig(
            exclude={"id", "created_at", "updated_at", "sprintlogs", "plugin_meta", "owner", "owner_id", "slug"},
        ),
    ]
]
ReadDTO = SQLAlchemyDTO[Annotated[Project, DTOConfig(exclude={"sprintlogs"})]]
