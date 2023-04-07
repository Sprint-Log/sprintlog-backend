# pyright: reportGeneralTypeIssues=false

from sqlalchemy.ext.asyncio import AsyncSession
from starlite import get  # pylint: disable=unused-import
from starlite import Controller, Dependency, Provide, delete, post, put
from starlite.status_codes import HTTP_200_OK

from app.domain.tasks import CreateDTO, ReadDTO, Repository, Service, Task, WriteDTO
from app.lib.repository.types import FilterTypes


def provides_service(db_session: AsyncSession) -> Service:
    """Constructs repository and service objects for the request."""
    return Service(Repository(session=db_session))


class ApiController(Controller):
    details = "/{index:uuid}"
    path = "/tasks"
    dependencies = {"service": Provide(provides_service)}
    tags = ["Tasks"]

    @get()
    async def tasklist(
        self,
        service: Service,
        filters: list[FilterTypes] = Dependency(skip_validation=True),
    ) -> list[ReadDTO]:
        """Get a list of Tasks."""
        return [ReadDTO.from_orm(item) for item in await service.list(*filters)]

    @post()
    async def create(self, data: CreateDTO, service: Service) -> ReadDTO:
        """Create an `Task`."""
        return ReadDTO.from_orm(await service.create(Task.from_dto(data)))

    @get(details)
    async def get(self, service: Service, col_id: str) -> ReadDTO:
        """Get Task by ID."""
        return ReadDTO.from_orm(await service.get(col_id))

    @put(details)
    async def update(self, data: WriteDTO, service: Service, col_id: str) -> ReadDTO:
        """Update an author."""
        return ReadDTO.from_orm(await service.update(col_id, Task.from_dto(data)))

    @delete(details, status_code=HTTP_200_OK)
    async def delete(self, service: Service, col_id: str) -> ReadDTO:
        """Delete Task by ID."""
        return ReadDTO.from_orm(await service.delete(col_id))
