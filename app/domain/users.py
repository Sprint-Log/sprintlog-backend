from typing import TYPE_CHECKING
from uuid import UUID

import sqlalchemy as sa
from litestar.contrib.sqlalchemy.base import AuditBase as Base
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import Mapped, registry, relationship
from sqlalchemy.orm import MappedColumn as MCol
from starlite_users.adapter.sqlalchemy.mixins import SQLAlchemyRoleMixin
from starlite_users.password import PasswordManager
from starlite_users.schema import (
    BaseRoleCreateDTO,
    BaseRoleReadDTO,
    BaseRoleUpdateDTO,
    BaseUserCreateDTO,
    BaseUserReadDTO,
    BaseUserUpdateDTO,
)
from starlite_users.service import BaseUserService

__all__ = [
    "Role",
    "RoleCreateDTO",
    "RoleReadDTO",
    "RoleUpdateDTO",
    "User",
    "UserCreateDTO",
    "UserReadDTO",
    "UserRole",
    "UserService",
    "UserUpdateDTO",
]


if TYPE_CHECKING:
    from app.domain.tasks import Task

password_manager = PasswordManager()


class Role(Base, SQLAlchemyRoleMixin):  # type: ignore
    ...


class User(Base):
    title: Mapped[str] = MCol(String(20))
    login_count: Mapped[int] = MCol(Integer(), default=0)
    roles: Mapped[Role] = relationship("Role", secondary="userrole", lazy="joined")
    tasks: Mapped[list["Task"] | None] = relationship(back_populates="assignee")


class UserRole(Base):
    """Base for all SQLAlchemy declarative models."""

    registry = registry(
        type_annotation_map={UUID: pg.UUID, dict: pg.JSONB},
    )
    user_id: Mapped[UUID] = MCol(sa.UUID(), ForeignKey("user.id"))
    role_id: Mapped[UUID] = MCol(sa.UUID(), ForeignKey("role.id"))


class RoleCreateDTO(BaseRoleCreateDTO):  # type: ignore
    pass


class RoleReadDTO(BaseRoleReadDTO):  # type: ignore
    pass


class RoleUpdateDTO(BaseRoleUpdateDTO):  # type: ignore
    pass


class UserCreateDTO(BaseUserCreateDTO):  # type: ignore
    title: str


class UserReadDTO(BaseUserReadDTO):  # type: ignore
    title: str
    login_count: int
    # we need override `roles` to display our custom RoleDTO fields
    roles: list[RoleReadDTO | None]


class UserUpdateDTO(BaseUserUpdateDTO):  # type: ignore
    title: str | None
    # we'll update `login_count` in the UserService.post_login_hook


class UserService(BaseUserService[User, UserCreateDTO, UserUpdateDTO, Role]):  # type: ignore
    async def post_login_hook(self, user: User) -> None:  # This will properly increment the user's `login_count`
        user.login_count += 1  # pyright: ignore
        await self.repository.session.commit()
