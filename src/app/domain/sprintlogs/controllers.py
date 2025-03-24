from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast, Dict, Annotated

from collections import defaultdict
from datetime import datetime
from dataclasses import dataclass
from collections.abc import Sequence

from litestar import Controller, delete, get, post, put
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.params import Dependency
from litestar.status_codes import HTTP_200_OK
from litestar.params import Dependency

from app.domain.accounts.guards import requires_active_user
from app.domain.sprintlogs.dependencies import provide_sprintlog_service

from app.db.models.enums import (
    ItemType,
    Priority,
    Progress,
    Status,
)
from app.domain.sprintlogs.dtos import ReadDTO, WriteDTO
from structlog import get_logger

from litestar.pagination import OffsetPagination
from app.domain.sprintlogs.service import SprintLogService
from app.lib.deps import create_filter_dependencies
from uuid import UUID
from app.domain.sprintlogs import urls

if TYPE_CHECKING:
    from advanced_alchemy.filters import FilterTypes, LimitOffset
    from app.db import models as m

__all__ = ["SprintLogController", "ActiveProject"]

logger = get_logger()


@dataclass
class ActiveProject:
    project_slug: str
    task_assigned: int = 0
    completed_task: int = 0
    remaining_task: int = 0
    task_due: int = 0


def log_info(message: str) -> None:
    logger.error(message)


class SprintLogController(Controller):
    dto = WriteDTO
    return_dto = ReadDTO

    dependencies = {"service": Provide(provide_sprintlog_service)} | create_filter_dependencies(
        {
            "id_filter": UUID,
            "search": "name,email",
            "pagination_type": "limit_offset",
            "pagination_size": 20,
            "created_at": True,
            "updated_at": True,
            "sort_field": "name",
            "sort_order": "asc",
        },
    )
    tags = ["Sprintlogs"]
    detail_route = "/detail/{row_id:uuid}"
    project_route = "/project/{project_type:str}"
    user_route = "/tasks/user/{user_id:uuid}"
    active_project_route = "/projects/user/{user_id:uuid}"
    slug_route = "{slug:str}"

    @get(urls.SPRINTLOG_LIST, guards=[requires_active_user])
    async def get_sprintlogs(
        self,
        service: SprintLogService,
        filters: Annotated[list[FilterTypes], Dependency(skip_validation=True)],
    ) -> Sequence[m.SprintLog]:
        return await service.list(*filters)

    @post(urls.SPRINTLOG_CREATE, guards=[requires_active_user])
    async def create_sprintlog(
        self,
        data: m.SprintLog,
        current_user: m.User,
        service: SprintLogService,
    ) -> m.SprintLog:
        if not data.owner_id:
            data.owner_id = current_user.id
        if not data.assignee_id:
            data.assignee_id = current_user.id
        return await service.create(data)

    @get(urls.SPRINTLOG_DETAIL, guards=[requires_active_user])
    async def retrieve(self, service: SprintLogService, row_id: UUID) -> m.SprintLog:
        return await service.get(row_id)

    @put(urls.SPRINTLOG_UPDATE, guards=[requires_active_user])
    async def update(
        self,
        data: m.SprintLog,
        current_user: m.User,
        service: SprintLogService,
        row_id: UUID,
    ) -> m.SprintLog:
        old_data = await service.get(row_id)
        if not data.owner_id:
            data.owner_id = current_user.id
        if not data.assignee_id:
            data.assignee_id = current_user.id
        return await service.update(data, row_id, old_data=old_data)

    @delete(urls.SPRINTLOG_DELETE, guards=[requires_active_user], status_code=HTTP_200_OK)
    async def delete(self, service: SprintLogService, row_id: UUID) -> m.SprintLog:
        return await service.delete(row_id)

    @get(urls.SPRINTLOG_BACKLOG_TASK_BY_PROJECT, guards=[requires_active_user])
    async def get_sprintlog_backlog_task_by_project(
        self,
        service: SprintLogService,
        project_type: str,
        limit_offset: LimitOffset,
    ) -> OffsetPagination[m.SprintLog]:
        """
        Get backlog if the project type is concat with '_backlog' and get task if the project type is concat with '_task'
        """
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

    @get(urls.SPRINTLOG_DETAIL_BY_SLUG, guards=[requires_active_user])
    async def get_sprintlog_by_slug(self, service: SprintLogService, slug: str) -> m.SprintLog:
        obj: m.SprintLog | None = await service.repository.get_by_slug(slug)
        if obj:
            return obj
        raise HTTPException(
            status_code=404,
            detail=f"Sprintlog.slug {slug} not available",
        )

    @get(urls.SPRINTLOG_PROJECT_BY_USER, guards=[requires_active_user])
    async def get_project_by_user(
        self, service: SprintLogService, user_id: UUID, limit_offset: LimitOffset
    ) -> OffsetPagination[ActiveProject]:
        sprintlogs = await service.list(assignee_id=user_id)

        active_projects_data = await self.get_active_projects(sprintlogs, limit_offset)

        return OffsetPagination(
            items=active_projects_data["projects"],
            total=active_projects_data["total"],
            limit=limit_offset.limit,
            offset=limit_offset.offset,
        )

    @get(urls.SPRINTLOG_TASK_BY_USER, guards=[requires_active_user])
    async def retrieve_tasks_by_user(self, service: SprintLogService, user_id: UUID) -> Sequence[m.SprintLog]:
        return await service.list(assignee_id=user_id)

    @put(urls.SPRINTLOG_PROGRESS_UP, guards=[requires_active_user])
    async def increase_progress(self, service: SprintLogService, slug: str) -> m.SprintLog:
        return await self._update_progress(service, slug, 1)

    @put(
        urls.SPRINTLOG_PROGRESS_COMPLETE,
        guards=[requires_active_user],
    )
    async def toggle_complete(self, service: SprintLogService, slug: str, current_user: m.User) -> m.SprintLog:
        if current_user.is_superuser:
            return await self._toggle_completion(service, slug, authorized=True)
        return await self._toggle_completion(service, slug)

    @put(urls.SPRINTLOG_PROGRESS_DOWN, guards=[requires_active_user])
    async def decrease_progress(self, service: SprintLogService, slug: str) -> m.SprintLog:
        return await self._update_progress(service, slug, -1)

    @put(urls.SPRINTLOG_PROGRESS_CIRCLE, guards=[requires_active_user])
    async def circle_progress(self, service: SprintLogService, slug: str) -> m.SprintLog:
        return await self._circle_progress(service, slug)

    @put(urls.SPRINTLOG_PRIORITY_CIRCLE, guards=[requires_active_user])
    async def circle_priority(self, service: SprintLogService, slug: str) -> m.SprintLog:
        return await self._circle_priority(service, slug, 0)

    @put(urls.SPRINTLOG_STATUS_CIRCLE, guards=[requires_active_user])
    async def circle_status(self, service: SprintLogService, slug: str) -> m.SprintLog:
        return await self.update_status(service, slug, 0)

    @put(urls.SPRINTLOG_SWITCH_TASK, guards=[requires_active_user])
    async def switch_to_backlog(self, service: SprintLogService, slug: str) -> m.SprintLog:
        return await self._update_type(service, slug, "task")

    @put(urls.SPRINTLOG_SWITCH_BACKLOG, guards=[requires_active_user])
    async def switch_to_task(self, service: SprintLogService, slug: str) -> m.SprintLog:
        return await self._update_type(service, slug, "backlog")

    async def get_active_projects(self, tasks: Sequence[m.SprintLog], limit_offset: LimitOffset) -> Dict[str, Any]:
        project_map = defaultdict(lambda: ActiveProject(project_slug=""))
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
            if sprintlog.status != Status.completed and sprintlog.due_date < datetime.now().date():
                project.task_due += 1

        # Calculating the remaining tasks for each project
        for project in project_map.values():
            project.remaining_task = project.task_assigned - project.completed_task

        paginated_projects = list(project_map.values())[offset : offset + limit]
        total_active_projects = len(project_map)

        return {"projects": paginated_projects, "total": total_active_projects}

    async def _update_progress(
        self,
        service: SprintLogService,
        slug: str,
        delta: int,
    ) -> m.SprintLog:
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
        service: SprintLogService,
        slug: str,
        authorized: bool = False,
    ) -> m.SprintLog:
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

    async def _circle_progress(self, service: SprintLogService, slug: str) -> m.SprintLog:
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

    async def _update_type(
        self,
        service: SprintLogService,
        slug: str,
        typ: str,
    ) -> m.SprintLog:
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

    async def _update_priority(
        self,
        service: SprintLogService,
        slug: str,
        delta: int,
    ) -> m.SprintLog:
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
        service: SprintLogService,
        slug: str,
        delta: int,
    ) -> m.SprintLog:
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

    async def update_status(
        self,
        service: SprintLogService,
        slug: str,
        delta: int,
    ) -> m.SprintLog:
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
