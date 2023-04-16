from typing import TYPE_CHECKING, Any, Generic

from litestar.contrib.sqlalchemy.repository import ModelT

__all__ = ["Service", "ServiceError"]


if TYPE_CHECKING:
    from litestar.contrib.repository.abc import AbstractRepository, FilterTypes


class ServiceError(Exception):
    """Base class for `Service` related exceptions."""


class Service(Generic[ModelT]):
    def __init__(self, repository: "AbstractRepository[ModelT]") -> None:
        """Generic Service object.

        Args:
            repository: Instance conforming to `AbstractRepository` interface.
        """
        self.repository = repository

    # noinspection PyMethodMayBeStatic
    async def authorize_create(self, data: ModelT) -> ModelT:
        """Control resource creation.

        Can use `self.user` here.

        Args:
            data: The object to be created.

        Returns:
            The object with restricted attribute values removed.
        """
        return data

    async def create(self, data: ModelT) -> ModelT:
        """Wraps repository instance creation.

        Args:
            data: Representation to be created.

        Returns:
            Representation of created instance.
        """
        data = await self.authorize_create(data)
        return await self.repository.add(data)

    # noinspection PyMethodMayBeStatic
    async def authorize_list(self) -> None:
        """Authorize collection access."""

    async def list(self, *filters: "FilterTypes", **kwargs: Any) -> list[ModelT]:
        """Wraps repository scalars operation.

        Args:
            *filters: Collection route filters.
            **kwargs: Keyword arguments for attribute based filtering.

        Returns:
            The list of instances retrieved from the repository.
        """
        await self.authorize_list()
        return await self.repository.list(*filters, **kwargs)

    async def authorize_update(self, id_: Any, data: ModelT) -> ModelT:
        """Authorize update of item.

        Args:
            id_: Identifier of the object to be updated.
            data: The object to be updated.

        Returns:
            ModelT
        """
        self.repository.set_id_attribute_value(id_, data)
        return data

    async def update(self, id_: Any, data: ModelT) -> ModelT:
        """Wraps repository update operation.

        Args:
            id_: Identifier of item to be updated.
            data: Representation to be updated.

        Returns:
            Updated representation.
        """
        data = await self.authorize_update(id_, data)
        return await self.repository.update(data)

    async def authorize_upsert(self, id_: Any, data: ModelT) -> ModelT:
        """Authorize upsert of item.

        Args:
            id_: The identifier of the resource to upsert.
            data: The object to be updated.

        Returns:
            ModelT
        """
        self.repository.set_id_attribute_value(id_, data)
        return data

    async def upsert(self, id_: Any, data: ModelT) -> ModelT:
        """Wraps repository upsert operation.

        Args:
            id_: Identifier of the object for upsert.
            data: Representation for upsert.

        Returns:
        -------
            Updated or created representation.
        """
        data = await self.authorize_upsert(id_, data)
        return await self.repository.upsert(data)

    async def authorize_get(self, id_: Any) -> None:
        """Authorize get of item.

        Args:
            id_: Identifier of item to be retrieved.
        """

    async def get(self, id_: Any) -> ModelT:
        """Wraps repository scalar operation.

        Args:
            id_: Identifier of instance to be retrieved.

        Returns:
            Representation of instance with identifier `id_`.
        """
        await self.authorize_get(id_)
        return await self.repository.get(id_)

    async def authorize_delete(self, id_: Any) -> None:
        """Authorize delete of item.

        Args:
            id_: Identifier of item to be retrieved.
        """

    async def delete(self, id_: Any) -> ModelT:
        """Wraps repository delete operation.

        Args:
            id_: Identifier of instance to be deleted.

        Returns:
            Representation of the deleted instance.
        """
        await self.authorize_delete(id_)
        return await self.repository.delete(id_)
