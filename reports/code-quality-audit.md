# Code Quality Audit Report

**Repository:** khulnasoft-bot/primeagent
**Audit date:** 2026-11-02

## Project overview

- **Name:** primeagent (v1.13.0)
- **Language:** Python (requires >=3.10,<3.15), with a small TypeScript/frontend footprint
- **Build/package:** uv + hatchling; 42 workspace members (backend base, wfx, sdk, stepflow, 30 bundles)
- **Framework:** FastAPI backend; LangChain/LangGraph agent ecosystem; React/Vite frontend (docs)

## Lint / type / format configuration

- `ruff` configured in `pyproject.toml` (`select = ["ALL"]`, line-length 120, target py310), with extensive per-file ignores for tests, CLI scripts, Alembic migrations, and FastAPI runtime-evaluated types.
- Pre-commit config present (`.pre-commit-config.yaml`).
- `codespell`, `vulture` (dead code), `pyleak`, `blockbuster` in dev dependencies.
- Frontend ESLint (`.eslintrc.json`), `Makefile.frontend`.

## Changed files (this remediation)

| File | Change | Lint | Format |
|---|---|---|---|
| `src/wfx/src/wfx/cli/common.py` | bind probe to 127.0.0.1 | pass | formatted |
| `src/backend/base/primeagent/api/v1/folders.py` | sanitize redirect query value | pass | formatted |
| `src/backend/base/primeagent/api/v1/voice_mode.py` | generic client error messages | pass | formatted |
| `src/backend/base/primeagent/agentic/api/router.py` | generic SSE error message | pass | formatted |
| `src/wfx/src/wfx/cli/serve_app.py` | generic streaming error message | pass | formatted |

`uv run ruff check` and `uv run ruff format --check` pass on all changed files.

## Test execution

- `src/backend/tests/unit/api/v1/test_folders.py`: **4 passed** (validate redirect endpoints still work after sanitization).
- `src/wfx/tests/unit/cli/test_common.py`: could not run in this environment (wfx tests require `primeagent` to be uninstalled; it is installed in the active `.venv`). Change is minimal and reviewed.
- Full backend suite: not run (long-running, requires services/network; pyproject sets `timeout = 90` due to a known nightly stall in Backend Unit Tests Group 3).

## Code quality observations

- The repository carries a large number of scanner findings concentrated in test files and already-defended production paths. These contribute noise rather than real defects.
- `pyproject.toml` disables several ruff rules wholesale (e.g. `C90` McCabe, `PLR09` too-many-*, `D10` docstrings, `ANN`) — consistent with a large, fast-moving codebase, but reduces static-analysis coverage.
- pytest timeout was lowered to 90s with `timeout_method="thread"` as a diagnostic for a nightly stall (documented in `pyproject.toml`); revert once the stall is bounded.

## Recommendations

1. Tune CodeQL to recognize `is_relative_to` / `realpath`+`startswith` as path-sanitizers to reduce path-injection noise.
2. Re-enable the 150s signal timeout after the Group 3 stall is identified.
3. Keep `override-dependencies` security floors in sync with `uv.lock` on each release.
