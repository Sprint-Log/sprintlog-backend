"""Application."""
from rich import get_console
from rich.traceback import install as rich_tracebacks

from app import asgi, cli, domain, lib, utils

__all__ = ["lib", "domain", "utils", "asgi", "cli"]

rich_tracebacks(
    console=get_console(),
    suppress=(
        "sqlalchemy",
        "click",
        "rich",
        "saq",
        "litestar",
        "rich_click",
    ),
    show_locals=False,
)
"""Pre-configured traceback handler.

Suppresses some of the frames by default to reduce the amount printed to
the screen.
"""
