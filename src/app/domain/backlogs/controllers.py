# ruff: noqa: B008
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from litestar import Controller, delete, get, post, put
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.params import Dependency
from litestar.status_codes import HTTP_200_OK

from app.domain.accounts.guards import requires_active_user
from app.domain.accounts.models import User
from app.domain.backlogs.dependencies import provides_service
from app.domain.backlogs.models import Backlog as Model
from app.domain.backlogs.models import PriorityEnum, ProgressEnum, ReadDTO, Service, StatusEnum, WriteDTO

if TYPE_CHECKING:
    from uuid import UUID

    from litestar.contrib.repository import FilterTypes
    from litestar.contrib.repository.filters import LimitOffset
from litestar.pagination import OffsetPagination

__all__ = [
    "ApiController",
]


validation_skip: Any = Dependency(skip_validation=True)


class ApiController(Controller):
    dto = WriteDTO
    return_dto = ReadDTO
    path = "/api/backlogs"
    dependencies = {"service": Provide(provides_service, sync_to_thread=False)}
    tags = ["Backlogs"]
    detail_route = "/detail/{row_id:uuid}"
    project_route = "/project/{project_type:str}"
    slug_route = "/slug/{slug:str}"
    guards = [requires_active_user]

    @get()
    async def filter(self, service: "Service", filters: list["FilterTypes"] = validation_skip) -> Sequence[Model]:
        return await service.list(*filters)

    @post()
    async def create(self, data: Model, current_user: User, service: "Service") -> Model:
        if not data.owner_id:
            data.owner_id = current_user.id
        if not data.assignee_id:
            data.assignee_id = current_user.id
        return await service.create(data)

    @get(detail_route)
    async def retrieve(self, service: "Service", row_id: "UUID") -> Model:
        return await service.get(row_id)

    @put(detail_route)
    async def update(self, data: Model, current_user: User, service: "Service", row_id: "UUID") -> Model:
        if not data.owner_id:
            data.owner_id = current_user.id
        if not data.assignee_id:
            data.assignee_id = current_user.id
        return await service.update(row_id, data)

    @delete(detail_route, status_code=HTTP_200_OK)
    async def delete(self, service: "Service", row_id: "UUID") -> Model:
        return await service.delete(row_id)

    @get(project_route)
    async def filter_by_project_type(
        self, service: "Service", project_type: str, limit_offset: "LimitOffset"
    ) -> "OffsetPagination[Model]":
        results, total = await service.list_and_count(limit_offset, project_type=project_type)
        return OffsetPagination(items=results, total=total, limit=limit_offset.limit, offset=limit_offset.offset)

    @get(slug_route)
    async def retrieve_by_slug(self, service: "Service", slug: str) -> Model:
        obj = await service.repository.get_by_slug(slug)
        if obj:
            return obj
        raise HTTPException(status_code=404, detail=f"Backlog.slug {slug} not available")

    async def _update_progress(self, service: "Service", slug: str, delta: int) -> Model:
        obj = await service.repository.get_by_slug(slug)
        progress_list = list(ProgressEnum)
        if obj:
            current_idx = progress_list.index(obj.progress)
            next_idx = current_idx + delta
            if next_idx < 0:
                next_idx = 0
            elif next_idx >= len(progress_list):
                next_idx = len(progress_list) - 1
            obj.progress = ProgressEnum(progress_list[next_idx])
            if obj.progress != ProgressEnum.full:
                obj.status = StatusEnum.started
            else:
                obj.status = StatusEnum.checked_in
            return await service.update(obj.id, obj)
        raise HTTPException(status_code=404, detail=f"Backlog.slug {slug} not available")

    @put(f"progress/up{slug_route}")
    async def increase_progress(self, service: "Service", slug: str) -> Model:
        return await self._update_progress(service, slug, 1)

    @put(f"progress/down{slug_route}")
    async def decrease_progress(self, service: "Service", slug: str) -> Model:
        return await self._update_progress(service, slug, -1)

    @put(f"progress/circle{slug_route}")
    async def circle_progress(self, service: "Service", slug: str) -> Model:
        return await self._update_progress(service, slug, 0)

    async def _update_priority(self, service: "Service", slug: str, delta: int) -> Model:
        obj = await service.repository.get_by_slug(slug)
        priority_list = list(PriorityEnum)
        if obj:
            current_idx = priority_list.index(obj.priority)
            next_idx = current_idx + delta
            if next_idx < 0:
                next_idx = 0
            elif next_idx >= len(priority_list):
                next_idx = len(priority_list) - 1
            obj.priority = PriorityEnum(priority_list[next_idx])
            return await service.update(obj.id, obj)
        raise HTTPException(status_code=404, detail=f"Backlog.slug {slug} not available")

    @put(f"priority/circle{slug_route}")
    async def circle_priority(self, service: "Service", slug: str) -> Model:
        return await self._update_priority(service, slug, 0)

    async def update_status(self, service: "Service", slug: str, delta: int) -> Model:
        obj = await service.repository.get_by_slug(slug)
        status_list = list(StatusEnum)
        if obj:
            current_idx = status_list.index(obj.status)
            next_idx = current_idx + delta
            if next_idx < 0:
                next_idx = 0
            elif next_idx >= len(status_list):
                next_idx = len(status_list) - 1
            obj.status = StatusEnum(status_list[next_idx])
            return await service.update(obj.id, obj)
        raise HTTPException(status_code=404, detail=f"Backlog.slug {slug} not available")

    @put(f"status/circle{slug_route}")
    async def circle_status(self, service: "Service", slug: str) -> Model:
        return await self.update_status(service, slug, 0)
