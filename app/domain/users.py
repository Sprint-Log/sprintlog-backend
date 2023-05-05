from typing import TYPE_CHECKING, Annotated

from litestar.contrib.sqlalchemy.base import AuditBase as Base
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.contrib.sqlalchemy.repository import SQLAlchemyRepository
from litestar.dto.factory import DTOConfig
from sqlalchemy import String
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import MappedColumn as MCol

from app.lib import service
from app.lib.mixins import SQLAlchemyUserMixin

# from sqlalchemy.dialects import postgresql as pg
__all__ = [
    "Role",
    "User",
    "ReadDTO",
    "Repository",
    "Service",
    "WriteDTO",
]

from app.domain.roles import Role

if TYPE_CHECKING:
    from app.domain.backlogs import Backlog


class User(Base, SQLAlchemyUserMixin):
    title: Mapped[str] = MCol(String(20))
    tasks: Mapped[list["Backlog"]] = relationship(back_populates="assignee")


class Repository(SQLAlchemyRepository[User]):
    model_type = User


class Service(service.Service[User]):
    repository_type = User


WriteDTO = SQLAlchemyDTO[
    Annotated[User, DTOConfig(exclude={"id", "created", "updated"})]
]
ReadDTO = SQLAlchemyDTO[User]
