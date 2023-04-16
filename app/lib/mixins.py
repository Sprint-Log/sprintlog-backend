from typing import TypeVar

from sqlalchemy import ARRAY, Boolean, String
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declarative_mixin,
    mapped_column,
)

__all__ = ["Base", "SQLAlchemyRoleMixin", "SQLAlchemyUserMixin"]


class Base(DeclarativeBase):
    pass


@declarative_mixin
class SQLAlchemyRoleMixin:
    """Base SQLAlchemy role mixin."""

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True)


@declarative_mixin
class SQLAlchemyUserMixin:
    """Base SQLAlchemy user mixin."""

    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(1024))
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)
    roles: Mapped[list[str] | None] = mapped_column(ARRAY(String()), nullable=True)


UserModelType = TypeVar("UserModelType", bound=SQLAlchemyUserMixin)
RoleModelType = TypeVar("RoleModelType", bound=SQLAlchemyRoleMixin)
