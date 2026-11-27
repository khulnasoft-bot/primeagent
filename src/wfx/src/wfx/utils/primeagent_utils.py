"""PrimeAgent environment utility functions."""

import importlib.util

from wfx.log.logger import logger


class _PrimeAgentModule:
    # Static variable
    # Tri-state:
    # - None: PrimeAgent check not performed yet
    # - True: PrimeAgent is available
    # - False: PrimeAgent is not available
    _available = None

    @classmethod
    def is_available(cls):
        return cls._available

    @classmethod
    def set_available(cls, value):
        cls._available = value


def has_primeagent_memory():
    """Check if primeagent.memory (with database support) and MessageTable are available."""
    # TODO: REVISIT: Optimize this implementation later
    # - Consider refactoring to use lazy loading or a more robust service discovery mechanism
    #   that can handle runtime availability changes.

    # Use cached check from previous invocation (if applicable)

    is_primeagent_available = _PrimeAgentModule.is_available()

    if is_primeagent_available is not None:
        return is_primeagent_available

    # First check (lazy load and cache check)

    module_spec = None

    try:
        module_spec = importlib.util.find_spec("primeagent")
    except ImportError:
        pass
    except (TypeError, ValueError) as e:
        logger.error(f"Error encountered checking for primeagent.memory: {e}")

    is_primeagent_available = module_spec is not None
    _PrimeAgentModule.set_available(is_primeagent_available)

    return is_primeagent_available


def has_primeagent_db_backend() -> bool:
    """Return True iff primeagent-backed memory calls have a real DB to hit.

    Requires both primeagent to be importable AND the registered database
    service to be a non-noop implementation. Evaluated on every call because
    the database service is typically registered *after* this module is first
    imported (e.g., from Component class definitions loaded before graph setup).
    """
    if not has_primeagent_memory():
        return False
    from wfx.services.database.service import NoopDatabaseService
    from wfx.services.deps import get_db_service

    try:
        return not isinstance(get_db_service(), NoopDatabaseService)
    except Exception:  # noqa: BLE001
        return False
