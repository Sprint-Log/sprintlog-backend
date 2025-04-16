from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from advanced_alchemy.base import UUIDAuditBase
from litestar.dto import Mark, dto_field
from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.enums import ChatType, EventType

__all__ = ["Chat"]

if TYPE_CHECKING:
    from .sprintLog import SprintLog


class Chat(UUIDAuditBase):
    __tablename__ = "chats"

    parent_id: Mapped[UUID | None] = mapped_column(ForeignKey("chats.id"), nullable=True)
    parent = relationship("Chat", remote_side="Chat.id", back_populates="replies", lazy="selectin", join_depth=2)
    replies = relationship("Chat", back_populates="parent", lazy="selectin", join_depth=2)

    sprint_id: Mapped[UUID | None] = mapped_column(ForeignKey("sprint_log.id"), nullable=False)
    chat_type: Mapped[ChatType] = mapped_column(ENUM(ChatType), nullable=False)
    event_type: Mapped[EventType] = mapped_column(ENUM(EventType), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    sprintlog: Mapped[SprintLog] = relationship("SprintLog", back_populates="chats")
    meta: Mapped[dict | None] = mapped_column(
        default=dict,
        info=dto_field(Mark.READ_ONLY),
    )
