# Remediation Summary

**Repository:** khulnasoft-bot/primeagent
**Audit date:** 2026-11-02
**Branch:** `main` (changes left uncommitted, not pushed)

## Changes implemented (this session)

| # | File | Finding | Severity | Fix |
|---|---|---|---|---|
| 1 | `src/wfx/src/wfx/cli/common.py:179` | `py/bind-socket-all-network-interfaces` | Medium | Port-availability probe now binds to `127.0.0.1` instead of all interfaces |
| 2 | `src/backend/base/primeagent/api/v1/folders.py` | `py/url-redirection` + CRLF injection | Medium | Added `_safe_query_value()` rejecting control chars; applied to `search` param |
| 3 | `src/wfx/src/wfx/cli/serve_app.py:1015` | `py/stack-trace-exposure` | Medium | Client now receives generic error; full detail logged server-side with `exc_info=True` |
| 4 | `src/backend/base/primeagent/api/v1/voice_mode.py:1478/1481/1486` | `py/stack-trace-exposure` | Medium | Client receives generic `"Failed to fetch voices"`; server retains logs |
| 5 | `src/backend/base/primeagent/agentic/api/router.py:488` | `py/stack-trace-exposure` | Medium | SSE error event now generic `"Assistant run failed"`; exception logged server-side |

## Preserved (pre-existing working-tree fixes, not overwritten)

- `src/wfx/src/wfx/components/files_and_knowledge/filesystem.py` — path-traversal defense (rejects absolute/`..`, re-normalizes hardlink check)
- `src/wfx/src/wfx/base/mcp/util.py` — removed overlapping Unicode ranges (`py/overly-large-range`)
- `docs/src/components/CopyPageButton.tsx` — backslash escaping (`js/incomplete-sanitization`)

## Verification

- `uv run ruff check` on all changed files: **pass**
- `uv run ruff format --check` on all changed files: **pass**
- `src/backend/tests/unit/api/v1/test_folders.py`: **7 passed** (4 original + 3 new regression tests for CRLF/header injection)
- Python syntax (ast.parse) on all changed files: **OK**
- wfx `test_common.py`: could not run (environment constraint: wfx tests require `primeagent` uninstalled)

## Regression tests added

| Test | Covers |
|---|---|
| `test_read_folder_redirect_rejects_crlf_in_search` | CRLF characters in `search` param rejected (HTTP 400) |
| `test_read_folder_redirect_rejects_control_chars_in_search` | Control characters (code < 0x20) in `search` rejected |
| `test_read_folder_redirect_allows_safe_search` | Normal `search` values still work |

## Findings not changed (documented as false positive / accepted risk / design decision)

- `py/weak-sensitive-data-hashing` ×2 — SHA-256 on high-entropy API keys/fingerprints, not passwords
- `py/clear-text-storage-sensitive-data` (`login.py`) — API key in HttpOnly/Secure/SameSite session cookie (design)
- `py/clear-text-logging-sensitive-data` — CI/migration/load-test scripts only
- Defended `py/path-injection` sites — already validated/containment-checked; CodeQL doesn't recognize sanitizers
- All test-file findings — not production attack surface

## Open PRs (require human review, not merged)

#13, #23, #25

## Remaining risks

- `login.py` API-key cookie storage — security/product team decision
- Open PRs #13/#23/#25 unreviewed
- CodeQL path-injection noise on defended paths

## Machine-readable manifest

See `reports/remediation-manifest.json`.
