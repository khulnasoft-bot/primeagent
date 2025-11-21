"""Enhanced ServiceManager that extends wfx's ServiceManager with primeagent features."""

from __future__ import annotations

import importlib
import inspect
from typing import TYPE_CHECKING

from wfx.log.logger import logger
from wfx.services.manager import NoFactoryRegisteredError
from wfx.services.manager import ServiceManager as BaseServiceManager
from wfx.utils.concurrency import KeyedMemoryLockManager

if TYPE_CHECKING:
    from primeagent.services.base import Service
    from primeagent.services.factory import ServiceFactory
    from primeagent.services.schema import ServiceType


__all__ = ["NoFactoryRegisteredError", "ServiceManager"]


class ServiceManager(BaseServiceManager):
    """Enhanced ServiceManager with primeagent factory system and dependency injection."""

    def __init__(self) -> None:
        super().__init__()
        self.register_factories()
        self.keyed_lock = KeyedMemoryLockManager()

    def register_factories(self, factories: list[ServiceFactory] | None = None) -> None:
        """Register all available service factories."""
        for factory in factories or self.get_factories():
            try:
                self.register_factory(factory)
            except Exception:  # noqa: BLE001
                logger.exception(f"Error initializing {factory}")

    def get(self, service_name: ServiceType, default: ServiceFactory | None = None) -> Service:
        """Get (or create) a service by its name with keyed locking."""
        with self.keyed_lock.lock(service_name):
            return super().get(service_name, default)

    @classmethod
    def get_factories(cls) -> list[ServiceFactory]:
        """Auto-discover and return all service factories."""
        from primeagent.services.factory import ServiceFactory
        from primeagent.services.schema import ServiceType

        service_names = [ServiceType(service_type).value.replace("_service", "") for service_type in ServiceType]
        base_module = "primeagent.services"
        factories = []

        for name in service_names:
            try:
                # Special handling for services that are in wfx module
                base_module = "wfx.services" if name in ["settings", "mcp_composer"] else "primeagent.services"
                module_name = f"{base_module}.{name}.factory"
                module = importlib.import_module(module_name)

                # Find all classes in the module that are subclasses of ServiceFactory
                for _, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, ServiceFactory) and obj is not ServiceFactory:
                        factories.append(obj())
                        break

            except Exception as exc:
                logger.exception(exc)
                msg = f"Could not initialize services. Please check your settings. Error in {name}."
                raise RuntimeError(msg) from exc

        return factories
