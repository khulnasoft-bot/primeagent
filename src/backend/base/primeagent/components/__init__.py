"""PrimeAgent Components module."""

from __future__ import annotations

from typing import Any

from wfx.components import __all__ as _wfx_all

__all__: list[str] = list(_wfx_all)


def __getattr__(attr_name: str) -> Any:
    """Forward attribute access to wfx.components."""
    from wfx import components

    return getattr(components, attr_name)


def __dir__() -> list[str]:
    """Forward dir() to wfx.components."""
    return list(__all__)
