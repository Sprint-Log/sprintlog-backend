
from __future__ import annotations


from advanced_alchemy.repository import (
    SQLAlchemyAsyncSlugRepository,
)
from advanced_alchemy.service import (
    SQLAlchemyAsyncRepositoryService,
)

from app.db import models as m



class RoleService(SQLAlchemyAsyncRepositoryService[m.Role]):
    """Handles database operations for users."""

    class Repository(SQLAlchemyAsyncSlugRepository[m.Role]):
        """User SQLAlchemy Repository."""

        model_type = m.Role
