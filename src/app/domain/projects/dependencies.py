"""Project Service Provider."""

from __future__ import annotations

import pkgutil
from typing import TYPE_CHECKING

import app.plugins
from app.config.base import get_settings
from app.domain.projects.services import ProjectService
from app.lib.deps import create_service_provider
from app.lib.plugin import ProjectPlugin

if TYPE_CHECKING:
    from typing import Set

settings = get_settings()


def load_plugins() -> Set[ProjectPlugin]:
    """Scan and load all enabled ProjectPlugins from app.plugins."""
    loaded_plugins = set()
    for _, plugin_name, _ in pkgutil.iter_modules(list(app.plugins.__path__)):
        if plugin_name not in settings.plugin.ENABLED:
            continue
        module = __import__(f"{app.plugins.__name__}.{plugin_name}", fromlist=["*"])
        for obj_name in dir(module):
            obj = getattr(module, obj_name)
            if isinstance(obj, type) and issubclass(obj, ProjectPlugin) and obj is not ProjectPlugin:
                loaded_plugins.add(obj())

    return loaded_plugins


# Pre-load the plugins
PLUGINS = load_plugins()


class ExtendedProjectService(ProjectService):
    """ProjectService subclass that automatically attaches scanned plugins."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plugins = PLUGINS


provide_project_service = create_service_provider(
    ExtendedProjectService,
    load=[],
    error_messages={"duplicate_key": "This project already exists.", "integrity": "Project operation failed."},
)
