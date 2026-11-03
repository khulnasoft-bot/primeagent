# Frontend architecture and performance seams

PrimeAgent is a React 19 + TypeScript Vite SPA. `src/index.tsx` loads i18n before mounting `customization/custom-App`, which delegates to `App` and a React Router data router.

## Render boundaries

- `App` owns the global theme class and the router-level Suspense fallback.
- `routes.tsx` owns route composition and is the main code-splitting boundary.
- Flow editing is the heaviest interactive surface and should not be part of the auth/dashboard entry chunk.
- Markdown, editors, grids, React Flow, PDF, and visualization dependencies are feature dependencies and should remain behind route or component boundaries.

## State and network

The application uses Zustand stores, React contexts, React Query, and controller hooks. High-frequency stream/event state should remain local to the consuming surface; avoid putting token-level updates in a provider that wraps the entire router. Requests must be cancellable and subscriptions must clean up on unmount.

## Performance strategy

1. Lazy-load route modules, especially flow, settings, file, and knowledge-base surfaces.
2. Keep feature CSS with the feature where Vite can split it.
3. Measure before adding memoization; use memoization at stable leaf boundaries only.
4. Virtualize conversations, execution logs, and tables when item counts can grow beyond a viewport.
5. Keep streaming updates batched and isolate the active message from completed messages.
6. Use transform/opacity animations and honor `prefers-reduced-motion`.
