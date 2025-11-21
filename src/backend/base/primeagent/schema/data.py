"""Data class for primeagent - imports from wfx.

This maintains backward compatibility while using the wfx implementation.
"""

from wfx.schema.data import Data, custom_serializer, serialize_data

__all__ = ["Data", "custom_serializer", "serialize_data"]
