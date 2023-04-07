from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import MappedColumn as MCol
from sqlalchemy.orm import relationship
from starlite_users.adapter.sqlalchemy.guid import GUID
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

from app.lib.orm import Base

if TYPE_CHECKING:
    import uuid

password_manager = PasswordManager()


class User(Base):
    title: Mapped[str] = MCol(String(20))
    login_count: Mapped[int] = MCol(Integer(), default=0)
    roles: Mapped["Role"] = relationship("Role", secondary="user_role", lazy="joined")


class Role(Base, SQLAlchemyRoleMixin):  # type: ignore
    ...


class UserRole(Base):
    user_id: Mapped["uuid.UUID"] = MCol(GUID(), ForeignKey("user.id"))
    role_id: Mapped["uuid.UUID"] = MCol(GUID(), ForeignKey("role.id"))


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
    async def post_login_hook(
        self, user: User
    ) -> None:  # This will properly increment the user's `login_count`
        user.login_count += 1  # pyright: ignore
        await self.repository.session.commit()
