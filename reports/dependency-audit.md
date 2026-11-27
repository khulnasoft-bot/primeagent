# Dependency Audit Report

**Repository:** khulnasoft-bot/primeagent
**Audit date:** 2026-11-02
**Package manager:** uv (Python), npm (frontend, minimal)

## Dependabot / vulnerability alerts

| Source | Count | Notes |
|---|---:|---|
| Dependabot alerts | 0 | `gh api .../dependabot/alerts` returned `[]` |
| Secret scanning | 0 | None |

No active Dependabot vulnerability alerts were reported for this repository.

## Security-pinned dependencies (from pyproject.toml)

The project proactively pins/floors several dependencies for security reasons (CVEs/GHSAs cited inline):

**`[dependency-groups].dev` and `[project].dependencies`:**
- `oauthlib>=4.0.0,<5.0.0` — CVE-2026-49264, CVE-2026-49265
- Bounded ranges for all `wfx-*` bundles (never exact pins, to avoid resolver conflicts)

**`[tool.uv] constraint-dependencies`:**
- `datamodel-code-generator>=0.81.0` — CVE-2026-107377
- `fsspec>=2026.6.0` — CVE-2026-104851
- `langgraph>=1.2.14` — GHSA-3fx2-cqw9-xr3c
- `langgraph-sdk>=0.4.6` — GHSA-fvww-7h3r-vfhp / CVE-2026-104873, GHSA-3fx2-cqw9-xr3c
- `litellm>=1.103.1,<2.0.0,!=1.104.0rc1,!=1.107.0` — GHSA-7hp6-4w63-5g45 (fixed in 1.103.1/1.104.0rc2)
- `multidict>=6.9.1` — GHSA-54p9-h82j-f925 / CVE-2026-104874
- `oauthlib>=4.0.0,<5.0.0` — CVE-2026-49264, CVE-2026-49265
- `pymongo>=4.18.2,<5.0.0` — CVE-2026-88029, CVE-2026-96747/48/49
- `tornado>=6.5.10,<7.0.0` — 6.5.8/6.5.9 security fixes

**`[tool.uv] override-dependencies` (force-upgraded transitive deps):**
- `orjson>=3.11.6`, `gunicorn>=25.3.0`, `pypdf>=6.19.0,<7.0.0`, `cryptography>=50.0.0` (GHSA-g6cj-pr64-35w5), `nltk>=3.10.3`, `Markdown>=3.8.0`, `playwright>=1.59.0`, `authlib>=1.9.1,<2.0.0`, `PyJWT>=2.15.1,<3.0.0` (CVE-2026-102266/67/71/72/74), `virtualenv>=21.14.2,<22.0.0`, `langchain-litellm==0.5.1`, `lxml>=6.1.0,<7.0.0` (CVE-2026-41066), `mako>=1.3.12,<2.0.0` (CVE-2026-44307), `urllib3>=2.8.0,<3.0.0` (CVE-2026-97688), `python-liquid>=2.2.0,<3.0.0` (CVE-2026-45017), `GitPython>=3.1.58` (multiple GHSA), `h2>=4.4.1` (CVE-2026-71554), `z3-solver<4.15.7`

**`[tool.uv.workspace]`:** 42 workspace members including `src/backend/base`, `src/wfx`, `src/sdk`, `src/primeagent-stepflow`, and 30 bundle packages.

## Dependency health

- Lockfile: `uv.lock` present and tracked.
- Frontend lockfile: `package-lock.json` tracked (commit `dbbb67a9`).
- No Dependabot alerts, no secret-scanning alerts.
- All flagged CVEs/GHSAs have corresponding version constraints in `pyproject.toml`.
- No dependency upgrades were required as part of this remediation (no vulnerable version currently resolved).

## Remaining dependency risks

- The repository pins many transitive dependencies via `override-dependencies`; these should be re-validated on each uv lockfile regeneration to ensure floors remain compatible.
- `primeagent-base==1.13.0` and bundle packages are workspace members; cross-bundle compatibility is verified by the `cross-bundle-test.yml` CI matrix.
