"""Primeagent ServiceManager that extends wfx's ServiceManager with enhanced features.

This maintains backward compatibility while using wfx as the foundation.
"""

from __future__ import annotations

# Import the enhanced manager that extends wfx
from primeagent.services.enhanced_manager import NoFactoryRegisteredError, ServiceManager

__all__ = ["NoFactoryRegisteredError", "ServiceManager"]


def initialize_settings_service() -> None:
    """Initialize the settings manager."""
    from wfx.services.manager import get_service_manager
    from wfx.services.settings import factory as settings_factory

    get_service_manager().register_factory(settings_factory.SettingsServiceFactory())


def initialize_session_service() -> None:
    """Initialize the session manager."""
    from wfx.services.manager import get_service_manager

    from primeagent.services.cache import factory as cache_factory
    from primeagent.services.session import factory as session_service_factory

    initialize_settings_service()

    get_service_manager().register_factory(cache_factory.CacheServiceFactory())

    get_service_manager().register_factory(session_service_factory.SessionServiceFactory())
