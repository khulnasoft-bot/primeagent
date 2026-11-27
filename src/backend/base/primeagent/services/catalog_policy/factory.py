"""Catalog-policy service factory."""

from __future__ import annotations

from typing import TYPE_CHECKING

from primeagent.services.factory import ServiceFactory
from primeagent.services.schema import ServiceType

if TYPE_CHECKING:
    from wfx.services.catalog_policy import BaseCatalogPolicyService

    from primeagent.services.catalog_policy.service import PrimeAgentCatalogPolicyService
    from primeagent.services.database.service import DatabaseService


class CatalogPolicyServiceFactory(ServiceFactory):
    """Create the PrimeAgent database-backed catalog-policy service."""

    name = ServiceType.CATALOG_POLICY_SERVICE.value

    service_class: type[PrimeAgentCatalogPolicyService]

    def __init__(self) -> None:
        from primeagent.services.catalog_policy.service import PrimeAgentCatalogPolicyService

        super().__init__(PrimeAgentCatalogPolicyService)

    def create(self, database_service: DatabaseService) -> BaseCatalogPolicyService:
        """Build a catalog-policy service using the injected database service."""
        from wfx.services.deps import get_policy_bundle_service

        return self.service_class(database_service, get_policy_bundle_service())
