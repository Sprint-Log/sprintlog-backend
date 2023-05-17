# ruff: noqa: B008
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from litestar import Controller, delete, get, post, put
from litestar.contrib.repository.filters import CollectionFilter
from litestar.di import Provide
from litestar.params import Dependency
from litestar.status_codes import HTTP_200_OK

from app.domain.backlogs.dependencies import provides_service
from app.domain.backlogs.models import Backlog as Model
from app.domain.backlogs.models import ReadDTO, Service, WriteDTO

if TYPE_CHECKING:
    from uuid import UUID

    from litestar.contrib.repository.abc import FilterTypes


__all__ = [
    "ApiController",
]


validation_skip: Any = Dependency(skip_validation=True)


class ApiController(Controller):
    dto = WriteDTO
    return_dto = ReadDTO
    path = "/backlogs"
    dependencies = {"service": Provide(provides_service)}
    tags = ["Backlogs"]
    DETAIL_ROUTE = "/detail/{col_id:uuid}"
    SLUG_ROUTE = "/project/{slug:str}"

    @get()
    async def filter(self, service: Service, filters: list["FilterTypes"] = validation_skip) -> Sequence[Model]:
        """Get a list of Models."""
        return await service.list(*filters)

    @post()
    async def create(self, data: Model, service: Service) -> Model:
        """Create an `Model`."""
        return await service.create(data)

    @get(DETAIL_ROUTE)
    async def retrieve(self, service: Service, col_id: "UUID") -> Model:
        """Get Model by ID."""
        return await service.get(col_id)

    @get(SLUG_ROUTE)
    async def retrieve_linked(self, service: Service, slug: str) -> Sequence[Model]:
        """Get Model by ID."""
        return await service.list(filters=CollectionFilter(field_name="project_slug", values=[slug]))

    @put(DETAIL_ROUTE)
    async def update(self, data: Model, service: Service, col_id: "UUID") -> Model:
        """Update an Model."""
        return await service.update(col_id, data)

    @delete(DETAIL_ROUTE, status_code=HTTP_200_OK)
    async def delete(self, service: Service, col_id: "UUID") -> Model:
        """Delete Author by ID."""
        return await service.delete(col_id)
