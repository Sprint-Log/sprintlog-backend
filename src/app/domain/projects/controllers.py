# pyright: reportGeneralTypeIssues=false

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from litestar import (
    Controller,
    delete,
    get,  # pylint: disable=unused-import
    post,
    put,
)
from litestar.di import Provide
from litestar.params import Dependency
from litestar.status_codes import HTTP_200_OK

from app.domain.accounts.guards import requires_active_user
from app.domain.accounts.models import User

if TYPE_CHECKING:
    from uuid import UUID

    from advanced_alchemy.filters import FilterTypes

    from app.domain.projects.models import ProjectService
from app.domain.projects.dependencies import provides_service
from app.domain.projects.models import Project as Model
from app.domain.projects.models import ReadDTO, WriteDTO

__all__ = ["ApiController"]


validation_skip: Any = Dependency(skip_validation=True)


class ApiController(Controller):
    dto = WriteDTO
    return_dto = ReadDTO
    path = "/api/projects"
    dependencies = {"service": Provide(provides_service, sync_to_thread=True)}
    tags = ["Projects API"]
    DETAIL_ROUTE = "/{row_id:uuid}"

    @get(guards=[requires_active_user])
    async def filter(
        self,
        service: "ProjectService",
        filters: list["FilterTypes"] = validation_skip,
    ) -> Sequence[Model]:
        """Get a list of Models."""
        return await service.list(*filters)

    @post(guards=[requires_active_user])
    async def create(
        self,
        data: Model,
        current_user: User,
        service: "ProjectService",
    ) -> Model:
        """Create an `Model`."""

        data.owner_id = current_user.id
        return await service.create(data)

    @get(DETAIL_ROUTE, guards=[requires_active_user])
    async def retrieve(self, service: "ProjectService", row_id: "UUID") -> Model:
        """Get Model by ID."""
        return await service.get(row_id)

    @put(DETAIL_ROUTE, guards=[requires_active_user])
    async def update(
        self,
        data: Model,
        current_user: User,
        service: "ProjectService",
        row_id: "UUID",
    ) -> Model:
        """Update an Model."""
        data.owner_id = current_user.id
        return await service.update(item_id=row_id, data=data)

    @delete(DETAIL_ROUTE, status_code=HTTP_200_OK, guards=[requires_active_user])
    async def delete(self, service: "ProjectService", row_id: "UUID") -> Model:
        """Delete Author by ID."""
        return await service.delete(row_id)
