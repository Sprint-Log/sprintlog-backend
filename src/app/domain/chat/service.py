from __future__ import annotations

from typing import Any
from structlog import getLogger

from advanced_alchemy.repository import (
    SQLAlchemyAsyncSlugRepository,
)
from advanced_alchemy.service import (
    SQLAlchemyAsyncRepositoryService,
)


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
