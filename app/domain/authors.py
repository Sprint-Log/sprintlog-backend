from datetime import date
from typing import Annotated
from uuid import UUID

from litestar.contrib.sqlalchemy.base import AuditBase
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from litestar.dto.factory import DTOConfig
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.lib import service

__all__ = [
    "Author",
    "ReadDTO",
    "Repository",
    "Service",
    "WriteDTO",
]


class Author(AuditBase):
    name: Mapped[str]
    dob: Mapped[date]
    country_id: Mapped[UUID | None] = mapped_column(ForeignKey("country.id"))


class Repository(SQLAlchemyAsyncRepository[Author]):
    model_type = Author


class Service(service.Service[Author]):
    repository_type = Repository


write_config = DTOConfig(exclude={"created", "updated", "nationality"})
WriteDTO = SQLAlchemyDTO[Annotated[Author, write_config]]
ReadDTO = SQLAlchemyDTO[Author]
