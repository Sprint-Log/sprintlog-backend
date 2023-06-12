from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any
from uuid import UUID

if TYPE_CHECKING:
    from app.domain.backlogs.models import Backlog
    from app.domain.projects.models import Project

__all__ = ["BacklogPlugin", "ProjectPlugin"]


class BacklogPlugin(ABC):
    @abstractmethod
    async def before_create(self, data: "Backlog | dict[str, Any]") -> "Backlog | dict[str, Any]":
        return data

    @abstractmethod
    async def after_create(self, data: "Backlog") -> "Backlog":
        return data

    @abstractmethod
    async def before_update(self, item_id: str, data: "Backlog | dict[str, Any]") -> "Backlog | dict[str, Any]":
        return data

    @abstractmethod
    async def after_update(self, data: "Backlog") -> "Backlog":
        return data

    @abstractmethod
    async def before_delete(self, item_id: UUID) -> UUID:
        return item_id

    @abstractmethod
    async def after_delete(self, data: "Backlog") -> "Backlog":
        return data


class ProjectPlugin(ABC):
    @abstractmethod
    async def before_create(self, data: "Project") -> None:
        pass

    @abstractmethod
    async def after_create(self, data: "Project") -> None:
        pass

    @abstractmethod
    async def before_update(self, item_id: str, data: "Project") -> None:
        pass

    @abstractmethod
    async def after_update(self, data: "Project") -> None:
        pass

    @abstractmethod
    async def before_delete(self, item_id: str) -> None:
        pass

    @abstractmethod
    async def after_delete(self, data: "Project") -> None:
        pass
