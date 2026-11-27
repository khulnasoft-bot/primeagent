# CI/CD Pipeline Templates

Ready-to-use workflow files for the Flow DevOps Toolkit.
Copy the files you need into your project's CI configuration.

## GitHub Actions

| File | Trigger | Secrets needed |
|------|---------|----------------|
| [`github-actions/primeagent-validate.yml`](github-actions/primeagent-validate.yml) | PR touching `flows/**/*.json` | None |
| [`github-actions/primeagent-test.yml`](github-actions/primeagent-test.yml) | PR touching flows or tests | `PRIMEAGENT_STAGING_API_KEY` |
| [`github-actions/primeagent-push.yml`](github-actions/primeagent-push.yml) | Push to `main` touching flows | `PRIMEAGENT_PROD_API_KEY` |

### Quick start

```bash
mkdir -p .github/workflows
cp github-actions/primeagent-validate.yml \
   github-actions/primeagent-test.yml \
   github-actions/primeagent-push.yml \
   .github/workflows/
```

Configure these in **Settings → Environments**:

**`staging`** environment (used by `primeagent-test.yml`):
| Name | Type | Value |
|------|------|-------|
| `PRIMEAGENT_STAGING_URL` | Variable | `https://staging.primeagent.example.com` |
| `PRIMEAGENT_STAGING_API_KEY` | Secret | your staging API key |

**`production`** environment (used by `primeagent-push.yml`):
| Name | Type | Value |
|------|------|-------|
| `PRIMEAGENT_PROD_URL` | Variable | `https://primeagent.example.com` |
| `PRIMEAGENT_PROD_API_KEY` | Secret | your production API key |
| `PRIMEAGENT_PROJECT_NAME` | Variable | `Production Flows` *(optional)* |

Add **Required reviewers** to the `production` environment to gate every deploy
behind a manual approval step.

---

## GitLab CI

| File | Description |
|------|-------------|
| [`gitlab-ci/primeagent.yml`](gitlab-ci/primeagent.yml) | Three-stage template: validate → test → deploy |

### Quick start

```bash
mkdir -p .gitlab/ci
cp gitlab-ci/primeagent.yml .gitlab/ci/
```

Add to your `.gitlab-ci.yml`:

```yaml
include:
  - local: .gitlab/ci/primeagent.yml
```

Configure these in **Settings → CI/CD → Variables**:

| Variable | Protected | Masked | Description |
|----------|-----------|--------|-------------|
| `PRIMEAGENT_STAGING_URL` | ✓ | ✗ | Staging instance URL |
| `PRIMEAGENT_STAGING_API_KEY` | ✓ | ✓ | Staging API key |
| `PRIMEAGENT_PROD_URL` | ✓ | ✗ | Production instance URL |
| `PRIMEAGENT_PROD_API_KEY` | ✓ | ✓ | Production API key |
| `PRIMEAGENT_PROJECT_NAME` | ✗ | ✗ | Project folder name *(optional)* |

---

## Shell scripts (`ci/`)

The `shell/` templates (`ci-validate.sh`, `ci-test.sh`, `ci-push.sh`) work with
any CI system (Jenkins, CircleCI, Bitbucket Pipelines, Azure Pipelines, etc.).
They are copied to `ci/` by `wfx init`.

### Environment variables

#### `ci-validate.sh`

| Variable | Default | Description |
|----------|---------|-------------|
| `FLOWS_DIR` | `flows/` | Directory containing flow JSON files |
| `VALIDATE_LEVEL` | `4` | Validation depth (1–4) |
| `VALIDATE_FORMAT` | `text` | Output format: `text` or `json` |
| `WFX_VERSION` | *(latest)* | PEP 508 version specifier for `wfx`, e.g. `>=0.4,<1` or `==1.2.3` |

#### `ci-test.sh`

| Variable | Default | Description |
|----------|---------|-------------|
| `PRIMEAGENT_URL` | — | URL of target PrimeAgent instance (Approach A) |
| `PRIMEAGENT_API_KEY` | — | API key for target instance (Approach A) |
| `PRIMEAGENT_ENV` | — | Environment name from config (Approach B) |
| `PRIMEAGENT_ENVIRONMENTS_FILE` | `primeagent-environments.toml` | Path to environments config (Approach B) |
| `TESTS_DIR` | `tests/` | Directory containing test files |
| `PYTEST_MARKERS` | `integration` | Markers passed to `pytest -m` |
| `PYTEST_ARGS` | — | Extra arguments forwarded verbatim to pytest |
| `SDK_VERSION` | *(latest)* | PEP 508 version specifier for `primeagent-sdk` |

#### `ci-push.sh`

| Variable | Default | Description |
|----------|---------|-------------|
| `PRIMEAGENT_URL` | — | URL of target PrimeAgent instance (Approach A) |
| `PRIMEAGENT_API_KEY` | — | API key for target instance (Approach A) |
| `PRIMEAGENT_ENV` | — | Environment name from config (Approach B) |
| `PRIMEAGENT_ENVIRONMENTS_FILE` | `primeagent-environments.toml` | Path to environments config (Approach B) |
| `FLOWS_DIR` | `flows/` | Directory containing flow JSON files |
| `PRIMEAGENT_PROJECT` | — | Project (folder) name on the remote instance |
| `PRIMEAGENT_PROJECT_ID` | — | Project UUID (takes precedence over `PRIMEAGENT_PROJECT`) |
| `DRY_RUN` | `false` | Set to `true` to preview without making changes |
| `WFX_VERSION` | *(latest)* | PEP 508 version specifier for `wfx` |

---

## How it all fits together

```
PR opened
  │
  ├── primeagent-validate  ──── wfx validate flows/ --level 4
  │                           ↳ blocks merge if any flow is malformed
  │
  └── primeagent-test  ──────── pytest tests/ --primeagent-env staging
                              ↳ skips gracefully if staging is unavailable

Merge to main
  │
  └── primeagent-push  ──────── wfx push --dir flows/ --env production
                              ↳ upserts every flow by stable ID
                              ↳ idempotent: safe to re-run
```

## Writing integration tests

Install the testing extra:

```bash
pip install "primeagent-sdk[testing]"
```

Create `tests/test_flows.py`:

```python
def test_rag_flow(flow_runner):
    response = flow_runner("rag-endpoint", "What is PrimeAgent?")
    assert "PrimeAgent" in response.first_text_output()

async def test_async_flow(async_flow_runner):
    response = await async_flow_runner("my-endpoint", "Hello!")
    assert response.first_text_output() is not None
```

Run locally against staging:

```bash
PRIMEAGENT_URL=https://staging.primeagent.example.com \
PRIMEAGENT_API_KEY=<key> \
pytest tests/ -m integration
```
