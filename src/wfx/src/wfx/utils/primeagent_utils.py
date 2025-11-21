"""Primeagent environment utility functions."""

import importlib.util

from wfx.log.logger import logger


class _PrimeagentModule:
    # Static variable
    # Tri-state:
    # - None: Primeagent check not performed yet
    # - True: Primeagent is available
    # - False: Primeagent is not available
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

    is_primeagent_available = _PrimeagentModule.is_available()

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
    _PrimeagentModule.set_available(is_primeagent_available)

    return is_primeagent_available
