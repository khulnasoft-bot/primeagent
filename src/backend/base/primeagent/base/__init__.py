"""Backwards compatibility module for primeagent.base.

This module imports from wfx.base to maintain compatibility with existing code
that expects to import from primeagent.base.
"""

# Import all base modules from wfx for backwards compatibility
from wfx.base import *  # noqa: F403
