# Frontend performance budgets

These are initial guardrails for the Vite frontend. Enforce them against production output and a fixed browser profile; do not compare development builds.

| Metric | Budget |
| --- | ---: |
| Initial JS transfer | 600 KB gzip |
| Initial CSS transfer | 150 KB gzip |
| Largest route JS asset | 2 MB gzip |
| LCP | <= 2.5 s |
| CLS | <= 0.1 |
| INP | <= 200 ms |
| Long tasks during route transition | <= 3 over 50 ms |

Feature chunks such as the flow editor may exceed the initial budget, but should be loaded only by the route that needs them. Record exceptions with a reason and owning feature.
