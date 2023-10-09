from __future__ import annotations

from typing import TYPE_CHECKING

from litestar import Controller, delete, get, patch, post
from litestar.di import Provide
from litestar.params import Dependency, Parameter

from app.domain import urls
from app.domain.accounts.guards import requires_active_user, requires_superuser
from app.domain.tags.dependencies import provide_tags_service
from app.domain.tags.dtos import TagCreateDTO, TagDTO
from app.lib import log

if TYPE_CHECKING:
    from uuid import UUID

    from advanced_alchemy.filters import FilterTypes
    from litestar.dto import DTOData
    from litestar.pagination import OffsetPagination

    from app.domain.tags.models import Tag
    from app.domain.tags.services import TagService


__all__ = ["TagController"]


logger = log.get_logger()


class TagController(Controller):
    """Handles the interactions within the Tag objects."""

    guards = [requires_active_user]
    dependencies = {"tags_service": Provide(provide_tags_service)}
    tags = ["Tags"]
    return_dto = TagDTO

    @get(
        operation_id="ListTags",
        name="tags:list",
        summary="List Tags",
        description="Retrieve the tags.",
        path=urls.TAG_LIST,
    )
    async def list_tags(
        self,
        tags_service: TagService,
        filters: list[FilterTypes] = Dependency(skip_validation=True),
    ) -> OffsetPagination[Tag]:
        """List tags."""
        results, total = await tags_service.list_and_count(*filters)
        return tags_service.to_dto(results, total, *filters)

    @get(
        operation_id="GetTag",
        name="tags:get",
        path=urls.TAG_DETAILS,
        summary="Retrieve the details of a tag.",
    )
    async def get_tag(
        self,
        tags_service: TagService,
        tag_id: UUID = Parameter(
            title="Tag ID",
            description="The tag to retrieve.",
        ),
    ) -> Tag:
        """Get a new migration tag."""
        db_obj = await tags_service.get(tag_id)
        return tags_service.to_dto(db_obj)

    @post(
        operation_id="CreateTag",
        name="tags:create",
        summary="Create a new tag.",
        cache_control=None,
        description="A tag is a place where you can upload and group collections of databases.",
        guards=[requires_superuser],
        path=urls.TAG_CREATE,
        dto=TagCreateDTO,
    )
    async def create_tag(
        self,
        tags_service: TagService,
        data: DTOData[Tag],
    ) -> Tag:
        """Create a new tag."""
        db_obj = await tags_service.create(data.create_instance())
        return tags_service.to_dto(db_obj)

    @patch(
        operation_id="UpdateTag",
        name="tags:update",
        path=urls.TAG_UPDATE,
        guards=[requires_superuser],
    )
    async def update_tag(
        self,
        tags_service: TagService,
        data: DTOData[Tag],
        tag_id: UUID = Parameter(
            title="Tag ID",
            description="The tag to update.",
        ),
    ) -> Tag:
        """Update a tag."""
        db_obj = await tags_service.update(item_id=tag_id, data=data.create_instance())
        return tags_service.to_dto(db_obj)

    @delete(
        operation_id="DeleteTag",
        name="tags:delete",
        path=urls.TAG_DELETE,
        summary="Remove Tag",
        description="Removes a tag and its associations",
        guards=[requires_superuser],
        return_dto=None,
    )
    async def delete_tag(
        self,
        tags_service: TagService,
        tag_id: UUID = Parameter(
            title="Tag ID",
            description="The tag to delete.",
        ),
    ) -> None:
        """Create a new migration tag."""
        _ = await tags_service.delete(tag_id)
