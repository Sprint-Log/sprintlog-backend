from typing import Annotated

from litestar.contrib.sqlalchemy.base import AuditBase as Base
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.contrib.sqlalchemy.repository import SQLAlchemyRepository
from litestar.dto.factory import DTOConfig

from app.lib import service
from app.lib.mixins import SQLAlchemyRoleMixin

# from sqlalchemy.dialects import postgresql as pg
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


class Repository(SQLAlchemyRepository[Role]):
    model_type = Role


class Service(service.Service[Role]):
    repository_type = Role


WriteDTO = SQLAlchemyDTO[Annotated[Role, DTOConfig(exclude={"id", "created", "updated"})]]
ReadDTO = SQLAlchemyDTO[Role]
