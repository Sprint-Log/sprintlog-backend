# pyright: reportGeneralTypeIssues=false

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

if TYPE_CHECKING:
    from uuid import UUID

    from litestar.contrib.repository.abc import FilterTypes
    from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.projects import Project as Model
from app.domain.projects import ReadDTO, Repository, Service, WriteDTO

__all__ = ["ApiController", "provides_service"]


def provides_service(db_session: "AsyncSession") -> Service:
    """Constructs repository and service objects for the request."""
    return Service(Repository(session=db_session))


validation_skip: Any = Dependency(skip_validation=True)


class ApiController(Controller):
    dto = WriteDTO
    return_dto = ReadDTO
    path = "/projects"
    dependencies = {"service": Provide(provides_service)}
    tags = ["Projects"]
    DETAIL_ROUTE = "/{col_id:uuid}"

    @get()
    async def filter(self, service: Service, filters: list["FilterTypes"] = validation_skip) -> list[Model]:
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

    @put(DETAIL_ROUTE)
    async def update(self, data: Model, service: Service, col_id: "UUID") -> Model:
        """Update an Model."""
        return await service.update(col_id, data)

    @delete(DETAIL_ROUTE, status_code=HTTP_200_OK)
    async def delete(self, service: Service, col_id: "UUID") -> Model:
        """Delete Author by ID."""
        return await service.delete(col_id)
