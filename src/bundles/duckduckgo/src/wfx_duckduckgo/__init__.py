"""wfx-duckduckgo: DuckDuckGo Search bundle.

This package is the distribution unit ``wfx-duckduckgo``.  At runtime
PrimeAgent's loader discovers ``extension.json`` shipped alongside this
``__init__.py`` and registers ``DuckDuckGoSearchComponent`` under the
namespaced ID ``ext:duckduckgo:DuckDuckGoSearchComponent@official``.

The first provider extracted from ``wfx.components.<provider>`` into
a standalone Bundle.
"""

from wfx_duckduckgo.components.duckduckgo.duck_duck_go_search_run import (
    DuckDuckGoSearchComponent,
)

__all__ = ["DuckDuckGoSearchComponent"]
