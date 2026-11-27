"""Authorization service factory."""

from __future__ import annotations

from typing import TYPE_CHECKING

from primeagent.services.factory import ServiceFactory
from primeagent.services.schema import ServiceType

if TYPE_CHECKING:
    from wfx.services.authorization.base import BaseAuthorizationService
    from wfx.services.settings.service import SettingsService

    from primeagent.services.authorization.service import PrimeAgentAuthorizationService


class AuthorizationServiceFactory(ServiceFactory):
    """Factory that creates the PrimeAgent authorization service."""

    name = ServiceType.AUTHORIZATION_SERVICE.value

    service_class: type[PrimeAgentAuthorizationService]

    def __init__(self) -> None:
        """Bind the factory to the PrimeAgentAuthorizationService implementation."""
        from primeagent.services.authorization.service import PrimeAgentAuthorizationService

        super().__init__(PrimeAgentAuthorizationService)

    def create(self, settings_service: SettingsService) -> BaseAuthorizationService:
        """Build a PrimeAgentAuthorizationService using the injected settings service."""
        return self.service_class(settings_service)
