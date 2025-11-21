# Backwards compatibility module for primeagent.events.event_manager
# This module redirects imports to the new wfx.events.event_manager module

from wfx.events.event_manager import (
    EventCallback,
    EventManager,
    PartialEventCallback,
    create_default_event_manager,
    create_stream_tokens_event_manager,
)

__all__ = [
    "EventCallback",
    "EventManager",
    "PartialEventCallback",
    "create_default_event_manager",
    "create_stream_tokens_event_manager",
]
