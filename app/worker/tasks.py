import json

from app.domain import tasks


async def task_created(_: dict, *, data: dict) -> None:
    """Send an email when a new Author is created.

    Args:
        _: SAQ context.
        data: The created author object.

    Returns:
        The author object.
    """
    await tasks.Service.create_zulip_topic(json.dumps(data))


async def task_updated(_: dict, *, data: dict) -> None:
    """Send an email when a new Author is created.

    Args:
        _: SAQ context.
        data: The created author object.

    Returns:
        The author object.
    """
    await tasks.Service.update_zulip_topic(json.dumps(data))


async def task_deleted(_: dict, *, data: dict) -> None:
    """Send an email when a new Author is created.

    Args:
        _: SAQ context.
        data: The created author object.

    Returns:
        The author object.
    """
    await tasks.Service.delete_zulip_topic(json.dumps(data))
