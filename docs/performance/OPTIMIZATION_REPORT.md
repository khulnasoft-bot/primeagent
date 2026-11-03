# Optimization report

## Implemented

- Added lazy route boundaries for flow editing, settings, files, knowledge bases, collections, and settings subpages.
- Moved React Flow's stylesheet from the global app shell to the flow route.
- Enabled default Web Vitals reporting with a `primeagent:performance` browser event and development diagnostics.
- Updated theme class handling to use a null-safe `classList.toggle`.

## Expected impact

Unauthenticated and dashboard routes no longer need to synchronously load the flow editor and settings feature graphs. Flow CSS is also requested only when the flow route is rendered. These changes reduce initial work structurally; exact byte and Core Web Vitals deltas must be measured from a completed production build.

## Not claimed

This pass does not claim chat virtualization, worker offloading, or log virtualization without tracing the relevant components and measuring their item-count behavior. Those are follow-up opportunities rather than implemented changes.
