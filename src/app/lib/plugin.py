from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any
from uuid import UUID

if TYPE_CHECKING:
    from app.domain.projects.models import Project
    from app.domain.sprintlogs.models import SprintLog

__all__ = ["SprintlogPlugin", "ProjectPlugin"]


class SprintlogPlugin(ABC):
    @abstractmethod
    async def before_create(self, data: "SprintLog") -> "SprintLog":
        return data

    @abstractmethod
    async def after_create(self, data: "SprintLog") -> "SprintLog":
        return data

    @abstractmethod
    async def before_update(
        self,
        item_id: Any | None,
        data: "SprintLog",
        old_data: "SprintLog|dict|None" = None,
    ) -> "SprintLog":
        return data

    @abstractmethod
    async def after_update(
        self,
        data: "SprintLog",
        old_data: "SprintLog|dict|None" = None,
    ) -> "SprintLog":
        return data

    @abstractmethod
    async def before_delete(self, item_id: UUID) -> UUID:
        return item_id

    @abstractmethod
    async def after_delete(self, data: "SprintLog") -> "SprintLog":
        return data


class ProjectPlugin(ABC):
    @abstractmethod
    async def before_create(self, data: "Project") -> "Project":
        return data

    @abstractmethod
    async def after_create(self, data: "Project") -> "Project":
        return data

    @abstractmethod
    async def before_update(
        self,
        item_id: UUID,
        data: "Project",
        old_data: "Project|None" = None,
    ) -> "Project":
        return data

    @abstractmethod
    async def after_update(self, data: "Project") -> "Project":
        return data

    @abstractmethod
    async def before_delete(self, item_id: UUID) -> UUID:
        return item_id

    @abstractmethod
    async def after_delete(self, data: "Project") -> "Project":
        return data
