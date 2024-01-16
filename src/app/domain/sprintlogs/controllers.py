# ruff: noqa: B008
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, cast, Dict, List

from litestar import Controller, delete, get, post, put
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.params import Dependency
from litestar.status_codes import HTTP_200_OK

from app.domain.accounts.guards import requires_active_user
from app.domain.accounts.models import User
from app.domain.sprintlogs.dependencies import provides_service
from app.domain.sprintlogs.models import (
    ItemType,
    Priority,
    Progress,
    ReadDTO,
    SprintlogService,
    Status,
    WriteDTO,
)
from app.domain.sprintlogs.models import SprintLog as Model
from app.lib import log
# from sqlalchemy import select, func
from collections import defaultdict
from datetime import datetime
from dataclasses import dataclass

if TYPE_CHECKING:
    from uuid import UUID

    from advanced_alchemy.filters import FilterTypes, LimitOffset
from litestar.pagination import OffsetPagination

__all__ = [
    "ApiController","ActiveProject"
]

logger = log.get_logger()

@dataclass
class ActiveProject:
    project_slug: str
    task_assigned: int = 0
    completed_task: int = 0
    remaining_task: int = 0
    task_due: int = 0

def log_info(message: str) -> None:
    logger.error(message)


validation_skip: Any = Dependency(skip_validation=True)


class ApiController(Controller):
    dto = WriteDTO
    return_dto = ReadDTO
    path = "/api/sprintlogs"
    dependencies = {"service": Provide(provides_service, sync_to_thread=False)}
    tags = ["Sprintlogs"]
    detail_route = "/detail/{row_id:uuid}"
    project_route = "/project/{project_type:str}"
    user_route = "/tasks/user/{user_id:uuid}"
    active_project_route = "/projects/user/{user_id:uuid}"
    slug_route = "{slug:str}"

    @get(guards=[requires_active_user])
    async def filter(
        self,
        service: "SprintlogService",
        filters: list["FilterTypes"] = validation_skip,
    ) -> Sequence[Model]:
        return await service.list(*filters)

    @post(guards=[requires_active_user])
    async def create(
        self,
        data: Model,
        current_user: User,
        service: "SprintlogService",
    ) -> Model:
        if not data.owner_id:
            data.owner_id = current_user.id
        if not data.assignee_id:
            data.assignee_id = current_user.id
        return await service.create(data)

    @get(detail_route, guards=[requires_active_user])
    async def retrieve(self, service: "SprintlogService", row_id: "UUID") -> Model:
        return await service.get(row_id)

    @put(detail_route, guards=[requires_active_user])
    async def update(
        self,
        data: Model,
        current_user: User,
        service: "SprintlogService",
        row_id: "UUID",
    ) -> Model:
        old_data = await service.get(row_id)
        if not data.owner_id:
            data.owner_id = current_user.id
        if not data.assignee_id:
            data.assignee_id = current_user.id
        return await service.update(data, row_id, old_data=old_data)

    @delete(detail_route, guards=[requires_active_user], status_code=HTTP_200_OK)
    async def delete(self, service: "SprintlogService", row_id: "UUID") -> Model:
        return await service.delete(row_id)

    @get(project_route, guards=[requires_active_user])
    async def filter_by_project_type(
        self,
        service: "SprintlogService",
        project_type: str,
        limit_offset: "LimitOffset",
    ) -> "OffsetPagination[Model]":
        results, total = await service.list_and_count(
            limit_offset,
            project_type=project_type,
        )
        return OffsetPagination(
            items=cast(list, results),
            total=total,
            limit=limit_offset.limit,
            offset=limit_offset.offset,
        )

    @get(f"/slug/{slug_route}", guards=[requires_active_user])
    async def retrieve_by_slug(self, service: "SprintlogService", slug: str) -> Model:
        obj: Model | None = await service.repository.get_by_slug(slug)
        if obj:
            return obj
        raise HTTPException(
            status_code=404,
            detail=f"Sprintlog.slug {slug} not available",
        )

    @get(active_project_route, guards=[requires_active_user])
    async def retrieve_project_by_user(self, service: "SprintlogService", user_id: "UUID", limit_offset: "LimitOffset") -> "OffsetPagination[ActiveProject]":
        sprintlogs = await service.list(assignee_id=user_id)
        
        active_projects_data = await self.get_active_projects(sprintlogs, limit_offset)
        
        print("offset limitation:")
        print(limit_offset.limit)

        return OffsetPagination(
            items=active_projects_data['projects'],
            total=active_projects_data['total'],
            limit=limit_offset.limit,
            offset=limit_offset.offset,
        )
        
    async def get_active_projects(self, tasks: List[Model]  , limit_offset: "LimitOffset") -> Dict[str, List[ActiveProject]]:
        project_map = defaultdict(lambda: ActiveProject(project_slug=''))
        limit = limit_offset.limit
        offset = limit_offset.offset

        for sprintlog in tasks:
            project_slug = sprintlog.project_slug

            if not project_map[project_slug].project_slug:
                project_map[project_slug].project_slug = project_slug

            project = project_map[project_slug]

            # Incrementing counts based on the sprintlog's status
            if sprintlog.status in [Status.new, Status.started, Status.checked_in]:
                project.task_assigned += 1
            elif sprintlog.status == Status.completed:
                project.completed_task += 1
                project.task_assigned += 1

            # Checking whether the task is due or not
            if (
                sprintlog.status != Status.completed
                and sprintlog.due_date < datetime.now().date()
            ):
                project.task_due += 1

        # Calculating the remaining tasks for each project
        for project in project_map.values():
            project.remaining_task = project.task_assigned - project.completed_task

        paginated_projects = list(project_map.values())[offset : offset + limit]
        total_active_projects = len(project_map)

        return {'projects': paginated_projects, 'total':total_active_projects }
        
    @get(user_route, guards=[requires_active_user])
    async def retrieve_tasks_by_user(self, service: "SprintlogService", user_id: "UUID") -> list[Model]:
        return await service.list(assignee_id=user_id)
         
    async def _update_progress(
        self,
        service: "SprintlogService",
        slug: str,
        delta: int,
    ) -> Model:
        obj = await service.repository.get_by_slug(slug)
        progress_list = list(Progress)
        if obj:
            current_idx = progress_list.index(obj.progress)
            next_idx = current_idx + delta
            if next_idx < 0:
                next_idx = 0
            elif next_idx >= len(progress_list):
                next_idx = len(progress_list) - 1
            obj.progress = Progress(progress_list[next_idx])
            if obj.progress != Progress.ready:
                obj.status = Status.started
            else:
                obj.status = Status.checked_in
            return await service.update(obj, obj.id)
        raise HTTPException(
            status_code=404,
            detail=f"Sprintlog.slug {slug} not available",
        )

    async def _toggle_completion(
        self,
        service: "SprintlogService",
        slug: str,
        authorized: bool = False,
    ) -> Model:
        obj = await service.repository.get_by_slug(slug)
        progress_list = list(Progress)
        if obj:
            current_idx = progress_list.index(obj.progress)
            next_idx = 0 if current_idx == len(progress_list) else len(progress_list) - 1
            obj.progress = Progress(progress_list[next_idx])
            if obj.status == Status.checked_in:
                obj.status = Status.completed if authorized else Status.checked_in
            else:
                obj.status = Status.checked_in
            return await service.update(obj, obj.id)
        raise HTTPException(
            status_code=404,
            detail=f"Sprintlog.slug {slug} not available",
        )

    async def _circle_progress(self, service: "SprintlogService", slug: str) -> Model:
        obj = await service.repository.get_by_slug(slug)
        progress_list = list(Progress)
        if obj:
            current_idx = progress_list.index(obj.progress)
            next_idx = current_idx + 1
            if next_idx < 0:
                next_idx = len(progress_list)
            elif next_idx >= len(progress_list):
                next_idx = 0
            obj.progress = Progress(progress_list[next_idx])
            if obj.progress != Progress.ready:
                obj.status = Status.started
            else:
                obj.status = Status.checked_in
            return await service.update(obj, obj.id)
        raise HTTPException(
            status_code=404,
            detail=f"Sprintlog.slug {slug} not available",
        )

    @put(f"progress/up/{slug_route}", guards=[requires_active_user])
    async def increase_progress(self, service: "SprintlogService", slug: str) -> Model:
        return await self._update_progress(service, slug, 1)

    @put(
        f"progress/complete/{slug_route}",
        guards=[requires_active_user],
    )
    async def toggle_complete(self, service: "SprintlogService", slug: str, current_user: User) -> Model:
        if current_user.is_superuser:
            return await self._toggle_completion(service, slug, authorized=True)
        return await self._toggle_completion(service, slug)

    async def _update_type(
        self,
        service: "SprintlogService",
        slug: str,
        typ: str,
    ) -> Model:
        obj = await service.repository.get_by_slug(slug)

        if obj:
            old_data = obj.to_dict()
            log_info("obj.type " + obj.type)
            obj.type = ItemType[typ]
            if typ == "backlog":
                obj.progress = Progress.empty
                obj.status = Status.started
            return await service.update(obj, obj.id, old_data=old_data)
        raise HTTPException(
            status_code=404,
            detail=f"Sprintlog.slug {slug} not available",
        )

    @put(f"switch/task/{slug_route}", guards=[requires_active_user])
    async def switch_to_backlog(self, service: "SprintlogService", slug: str) -> Model:
        return await self._update_type(service, slug, "task")

    @put(f"switch/backlog/{slug_route}", guards=[requires_active_user])
    async def switch_to_task(self, service: "SprintlogService", slug: str) -> Model:
        return await self._update_type(service, slug, "backlog")

    @put(f"progress/down/{slug_route}", guards=[requires_active_user])
    async def decrease_progress(self, service: "SprintlogService", slug: str) -> Model:
        return await self._update_progress(service, slug, -1)

    @put(f"progress/circle/{slug_route}", guards=[requires_active_user])
    async def circle_progress(self, service: "SprintlogService", slug: str) -> Model:
        return await self._circle_progress(service, slug)

    async def _update_priority(
        self,
        service: "SprintlogService",
        slug: str,
        delta: int,
    ) -> Model:
        obj = await service.repository.get_by_slug(slug)
        priority_list = list(Priority)
        if obj:
            current_idx = priority_list.index(obj.priority)
            next_idx = current_idx + delta
            if next_idx < 0:
                next_idx = 0
            elif next_idx >= len(priority_list):
                next_idx = len(priority_list) - 1
            obj.priority = Priority(priority_list[next_idx])
            return await service.update(obj, obj.id)
        raise HTTPException(
            status_code=404,
            detail=f"Sprintlog.slug {slug} not available",
        )

    async def _circle_priority(
        self,
        service: "SprintlogService",
        slug: str,
        delta: int,
    ) -> Model:
        obj = await service.repository.get_by_slug(slug)
        priority_list = list(Priority)
        if obj:
            current_idx = priority_list.index(obj.priority)
            next_idx = current_idx + 1
            if next_idx < 0:
                next_idx = len(priority_list)
            elif next_idx >= len(priority_list):
                next_idx = 0
            obj.priority = Priority(priority_list[next_idx])
            return await service.update(obj, obj.id)
        raise HTTPException(
            status_code=404,
            detail=f"Sprintlog.slug {slug} not available",
        )

    @put(f"priority/circle/{slug_route}", guards=[requires_active_user])
    async def circle_priority(self, service: "SprintlogService", slug: str) -> Model:
        return await self._circle_priority(service, slug, 0)

    async def update_status(
        self,
        service: "SprintlogService",
        slug: str,
        delta: int,
    ) -> Model:
        obj = await service.repository.get_by_slug(slug)
        status_list = list(Status)
        if obj:
            current_idx = status_list.index(obj.status)
            next_idx = current_idx + delta
            if next_idx < 0:
                next_idx = 0
            elif next_idx >= len(status_list):
                next_idx = len(status_list) - 1
            obj.status = Status(status_list[next_idx])
            return await service.update(obj, obj.id)
        raise HTTPException(
            status_code=404,
            detail=f"Sprintlog.slug {slug} not available",
        )

    @put(f"status/circle/{slug_route}", guards=[requires_active_user])
    async def circle_status(self, service: "SprintlogService", slug: str) -> Model:
        return await self.update_status(service, slug, 0)
