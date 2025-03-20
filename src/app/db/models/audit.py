from uuid import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from advanced_alchemy.base import UUIDAuditBase

__all__ = ["Audit"]


class Audit(UUIDAuditBase):
    __tablename__ = "audit"
    backlog_id: Mapped[UUID] = mapped_column(ForeignKey("sprint_log.id"))
    field_name: Mapped[str]
    old_value: Mapped[str]
    new_value: Mapped[str]
