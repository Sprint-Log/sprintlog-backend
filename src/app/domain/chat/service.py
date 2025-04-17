from __future__ import annotations

from typing import Any
from structlog import getLogger

from advanced_alchemy.repository import (
    SQLAlchemyAsyncSlugRepository,
)
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from app.db import models as m
from uuid import UUID
from app.domain.chat.schemas import Chat as ChatSchema

__all__ = ["ChatService"]

logger = getLogger()


class ChatService(SQLAlchemyAsyncRepositoryService[m.Chat]):
    """Handles database operations for chats."""

    class ChatRepository(SQLAlchemyAsyncSlugRepository[m.Chat]):
        """Chat SQLAlchemy Repository."""

        slug_field = "slug"
        model_type = m.Chat

    repository_type = ChatRepository

    def __init__(self, **repo_kwargs: Any) -> None:

        super().__init__(**repo_kwargs)

        self.model_type = self.repository.model_type

    def to_chat_schema(self, chat: m.Chat) -> ChatSchema:
        return ChatSchema(
            id=chat.id,
            message=chat.message,
            chat_type=chat.chat_type,
            event_type=chat.event_type,
            sprint_id=chat.sprint_id,
            parent_id=chat.parent_id,
            parent=None,
            replies=[self.to_chat_schema(reply) for reply in chat.replies or []],
        )

    def _build_selectinload_chain(self, relationship_name: str, depth: int):
        option = selectinload(getattr(m.Chat, relationship_name))
        for _ in range(depth - 1):
            option = option.selectinload(getattr(m.Chat, relationship_name))
        return option

    async def get_nested_chats(self, sprint_id: UUID, max_depth: int = 4) -> tuple[list[m.Chat], int]:
        replies_option = self._build_selectinload_chain("replies", max_depth)
        logger.info("replies_option")
        logger.info(replies_option)
        stmt = (
            select(m.Chat)
            .options(replies_option)
            .where(and_(m.Chat.parent_id.is_(None), m.Chat.sprint_id == sprint_id))
        )
        result = await self.repository.session.execute(stmt)
        chats = result.scalars().all()
        return chats, len(chats)
