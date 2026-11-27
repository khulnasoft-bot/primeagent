"""Logical groupings of PrimeAgent settings.

Each module defines a ``BaseModel`` mixin that owns a cohesive subset of fields
plus their intra-group validators. They are composed into the final
``Settings`` class in :mod:`wfx.services.settings.base`.

Mixins inherit from ``BaseModel`` (not ``BaseSettings``) and are not intended
to be instantiated directly.
"""

from wfx.services.settings.groups.cache import CacheSettings
from wfx.services.settings.groups.components import ComponentsSettings
from wfx.services.settings.groups.database import DatabaseSettings
from wfx.services.settings.groups.mcp import McpSettings
from wfx.services.settings.groups.observability import ObservabilitySettings
from wfx.services.settings.groups.paths import PathSettings
from wfx.services.settings.groups.runtime import RuntimeSettings
from wfx.services.settings.groups.security import SecuritySettings
from wfx.services.settings.groups.server import ServerSettings
from wfx.services.settings.groups.storage import StorageSettings
from wfx.services.settings.groups.telemetry import TelemetrySettings
from wfx.services.settings.groups.ui import UiSettings
from wfx.services.settings.groups.variables import VariablesSettings

__all__ = [
    "CacheSettings",
    "ComponentsSettings",
    "DatabaseSettings",
    "McpSettings",
    "ObservabilitySettings",
    "PathSettings",
    "RuntimeSettings",
    "SecuritySettings",
    "ServerSettings",
    "StorageSettings",
    "TelemetrySettings",
    "UiSettings",
    "VariablesSettings",
]
