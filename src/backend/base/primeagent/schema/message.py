"""Message class for primeagent - imports from wfx.

This maintains backward compatibility while using the wfx implementation.
"""

# Import and re-export to ensure class identity is preserved
from wfx.schema.message import ContentBlock, DefaultModel, ErrorMessage, Message, MessageResponse

__all__ = ["ContentBlock", "DefaultModel", "ErrorMessage", "Message", "MessageResponse"]
