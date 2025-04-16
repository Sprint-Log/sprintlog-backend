"""User Account Controllers."""

from __future__ import annotations

from sqlalchemy.orm import selectinload

from app.db import models as m
from app.domain.accounts.services import UserService
from app.lib.deps import create_service_provider


__all__ = ["provide_chat_service"]

provide_chat_service = create_service_provider(
    UserService,
    load=[selectinload(m.Chat.sprintlog), selectinload(m.Chat.parent), selectinload(m.Chat.replies)],
    error_messages={"duplicate_key": "This chat already exists.", "integrity": "Chat operation failed."},
)
