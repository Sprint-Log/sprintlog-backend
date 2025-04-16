from __future__ import annotations

from typing import Any
from structlog import getLogger

from advanced_alchemy.repository import (
    SQLAlchemyAsyncSlugRepository,
)
from advanced_alchemy.service import (
    SQLAlchemyAsyncRepositoryService,
)
from app.domain.chat.schemas import Chat as ChatSchema

from app.db import models as m

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
