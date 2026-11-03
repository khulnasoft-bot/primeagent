# Frontend performance baseline

## Scope

Baseline captured from the Vite frontend in `src/frontend` on 2026-11-04.

## Findings

- The first production build transformed 8,156 modules and reached the default Node heap limit before emitting output. This is a build-memory failure, not a runtime measurement.
- Tailwind reports mixed `rem` and `px` screen units, which disables `min-*` and `max-*` variants.
- `src/frontend/src/routes.tsx` eagerly imported the flow editor, settings pages, files/knowledge pages, and their transitive dependencies.
- `@xyflow/react` CSS was loaded from the root app shell even for login and dashboard routes.
- Web Vitals reporting was effectively disabled because `reportWebVitals()` was called without a handler.

## Measurement limitations

No credible before/after Core Web Vitals or bundle-size comparison is claimed yet because the baseline build did not complete and the preview was not available during the audit. Production measurements should be collected with `agent-browser vitals` against the built preview at a fixed viewport and documented alongside the commit.

## Baseline commands

```bash
cd src/frontend
NODE_OPTIONS=--max-old-space-size=4096 npm run build
npm run type-check
npm run lint
npm test -- --runInBand
```
