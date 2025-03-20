
from uuid import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from advanced_alchemy.base import UUIDAuditBase

from app.db.models import SprintLog


class Audit(UUIDAuditBase):
    backlog_id: Mapped[UUID] = mapped_column(ForeignKey(SprintLog.id))
    field_name: Mapped[str]
    old_value: Mapped[str]
    new_value: Mapped[str]