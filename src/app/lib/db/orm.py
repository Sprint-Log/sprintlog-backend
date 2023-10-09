"""Application ORM configuration."""

from __future__ import annotations

from typing import Any

from advanced_alchemy.base import AuditColumns, orm_registry
from advanced_alchemy.base import UUIDAuditBase as TimestampedDatabaseModel
from advanced_alchemy.base import UUIDBase as DatabaseModel
from advanced_alchemy.repository.typing import ModelT
from sqlalchemy import String
from sqlalchemy.orm import (
    Mapped,
    declarative_mixin,
    mapped_column,
)

__all__ = ["DatabaseModel", "TimestampedDatabaseModel", "orm_registry", "model_from_dict", "AuditColumns", "SlugKey"]


@declarative_mixin
class SlugKey:
    """Slug unique Field Model Mixin."""

    __abstract__ = True
    slug: Mapped[str] = mapped_column(String(length=100), index=True, nullable=False, unique=True, sort_order=-9)


def model_from_dict(model: ModelT, **kwargs: Any) -> ModelT:
    """Return ORM Object from Dictionary."""
    data = {}
    for column in model.__table__.columns:
        column_val = kwargs.get(column.name, None)
        if column_val is not None:
            data[column.name] = column_val
    return model(**data)  # type: ignore
