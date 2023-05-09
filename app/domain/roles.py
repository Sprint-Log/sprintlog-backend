from typing import Annotated

from litestar.contrib.sqlalchemy.base import AuditBase as Base
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from litestar.dto.factory import DTOConfig

from app.lib import service
from app.lib.mixins import SQLAlchemyRoleMixin

__all__ = [
    "Role",
    # "RoleCreateDTO",
    # "RoleReadDTO",
    # "RoleUpdateDTO",
    # "UserCreateDTO",
    # "UserReadDTO",
    # "UserRole",
    # "UserService",
    # "UserUpdateDTO",
    "ReadDTO",
    "Repository",
    "Service",
    "WriteDTO",
]


class Role(Base, SQLAlchemyRoleMixin):
    ...


class Repository(SQLAlchemyAsyncRepository[Role]):
    model_type = Role


class Service(service.Service[Role]):
    repository_type = Role


WriteDTO = SQLAlchemyDTO[Annotated[Role, DTOConfig(exclude={"id", "created", "updated"})]]
ReadDTO = SQLAlchemyDTO[Role]
