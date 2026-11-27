# wfx-duckduckgo

DuckDuckGo Search component as a standalone PrimeAgent Extension Bundle.

This is the first provider extracted from `wfx.components.<provider>`
into a separate distribution.  The bundle ships a single component,
`DuckDuckGoSearchComponent`, which performs DuckDuckGo web searches
via `langchain-community`.

## Install

```bash
pip install wfx-duckduckgo
```

The bundle is registered automatically via the `primeagent.extensions`
entry-point.  After install, restart your PrimeAgent server; the
`DuckDuckGoSearchComponent` will appear in the palette under the
`duckduckgo` bundle group.

## Develop

```bash
cd src/bundles/duckduckgo
pip install -e .
wfx extension validate .
```

## Manifest

The extension manifest is shipped at
`src/wfx_duckduckgo/extension.json` and points at the bundle at
`components/duckduckgo`.  Components register under the canonical
namespaced ID `ext:duckduckgo:DuckDuckGoSearchComponent@official`.

## Migration

Saved flows referencing the legacy class name `DuckDuckGoSearchComponent`
or the old import path
`wfx.components.duckduckgo.duck_duck_go_search_run.DuckDuckGoSearchComponent`
are rewritten to the new namespaced ID by the migration table in
`src/wfx/src/wfx/extension/migration/migration_table.json`.
