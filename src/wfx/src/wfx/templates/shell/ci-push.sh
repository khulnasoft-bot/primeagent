#!/usr/bin/env bash
# ci-push.sh
#
# PURPOSE
#   Push (upsert) PrimeAgent flow JSON files to a remote PrimeAgent instance
#   using `wfx push`.  Stable flow IDs mean re-running always converges.
#
# USAGE
#   chmod +x ci-push.sh
#   export PRIMEAGENT_URL=https://staging.primeagent.example.com
#   export PRIMEAGENT_API_KEY=<your-api-key>
#   ./ci-push.sh
#
# ENVIRONMENT VARIABLES — connection (pick one approach)
#
#   Approach A: direct URL + key (simplest)
#     PRIMEAGENT_URL        URL of the target PrimeAgent instance.
#     PRIMEAGENT_API_KEY    API key for that instance.
#
#   Approach B: named environment from a TOML config
#     PRIMEAGENT_ENV                 Name of the environment block.
#                                  e.g. staging  or  production
#     PRIMEAGENT_ENVIRONMENTS_FILE   Path to environments TOML.
#                                  Default: primeagent-environments.toml
#     <api_key_env var>            The env var named in api_key_env inside the
#                                  TOML block.  Must be exported separately.
#
#   The TOML format:
#
#     [environments.staging]
#     url         = "https://staging.primeagent.example.com"
#     api_key_env  = "PRIMEAGENT_STAGING_API_KEY"
#
#     [environments.production]
#     url         = "https://primeagent.example.com"
#     api_key_env  = "PRIMEAGENT_PROD_API_KEY"
#
# ENVIRONMENT VARIABLES — behaviour
#   FLOWS_DIR            Directory containing flow JSON files.
#                        Default: flows/
#   PRIMEAGENT_PROJECT     Project (folder) name on the remote instance.
#                        Default: (no project — flows go to the default folder)
#   PRIMEAGENT_PROJECT_ID  Project UUID.  Takes precedence over PRIMEAGENT_PROJECT.
#   DRY_RUN              Set to "true" to show what would be pushed without
#                        making any changes.  Default: false
#   WFX_VERSION          wfx PEP 508 version specifier suffix appended directly
#                        to the package name, e.g. ">=0.4,<1" or "==1.2.3".
#                        Default: installs latest.
#
# EXIT CODES
#   0  All flows pushed (or dry-run completed) successfully
#   1  One or more flows failed to push
#
# INTEGRATIONS
#   Jenkins:          sh 'ci-push.sh'
#   CircleCI:         - run: bash ci-push.sh
#   Bitbucket:        - bash ci-push.sh
#   Azure Pipelines:  - script: bash ci-push.sh

set -euo pipefail

# ── Configuration ─────────────────────────────────────────────────────────── #

FLOWS_DIR="${FLOWS_DIR:-flows/}"
PRIMEAGENT_ENV="${PRIMEAGENT_ENV:-}"
PRIMEAGENT_ENVIRONMENTS_FILE="${PRIMEAGENT_ENVIRONMENTS_FILE:-primeagent-environments.toml}"
PRIMEAGENT_URL="${PRIMEAGENT_URL:-}"
PRIMEAGENT_API_KEY="${PRIMEAGENT_API_KEY:-}"
PRIMEAGENT_PROJECT="${PRIMEAGENT_PROJECT:-}"
PRIMEAGENT_PROJECT_ID="${PRIMEAGENT_PROJECT_ID:-}"
DRY_RUN="${DRY_RUN:-false}"
WFX_VERSION="${WFX_VERSION:-}"

# Normalise WFX_VERSION: if it looks like a bare version (starts with a digit),
# prepend "==" so the pip specifier is valid.
if [[ -n "${WFX_VERSION}" && "${WFX_VERSION}" =~ ^[0-9] ]]; then
  WFX_VERSION="==${WFX_VERSION}"
fi

# ── Install wfx ───────────────────────────────────────────────────────────── #

echo "==> Installing wfx${WFX_VERSION:+ ${WFX_VERSION}} ..."
pip install --quiet "wfx${WFX_VERSION}" primeagent-sdk

# ── Build environments file if using Approach B ───────────────────────────── #

if [[ -n "${PRIMEAGENT_ENV}" && ! -f "${PRIMEAGENT_ENVIRONMENTS_FILE}" ]]; then
  ENV_UPPER="${PRIMEAGENT_ENV^^}"
  ENV_UPPER="${ENV_UPPER//-/_}"
  URL_VAR="PRIMEAGENT_${ENV_UPPER}_URL"
  KEY_VAR="PRIMEAGENT_${ENV_UPPER}_API_KEY"

  echo "==> Writing ${PRIMEAGENT_ENVIRONMENTS_FILE} for environment '${PRIMEAGENT_ENV}' ..."
  printf '[environments.%s]\nurl = "%s"\napi_key_env = "%s"\n' \
    "${PRIMEAGENT_ENV}" \
    "${!URL_VAR:-}" \
    "${KEY_VAR}" \
    > "${PRIMEAGENT_ENVIRONMENTS_FILE}"
  export PRIMEAGENT_ENVIRONMENTS_FILE
fi

# ── Build wfx push command ────────────────────────────────────────────────── #

PUSH_CMD=(wfx push --dir "${FLOWS_DIR}")

if [[ -n "${PRIMEAGENT_ENV}" ]]; then
  PUSH_CMD+=(--env "${PRIMEAGENT_ENV}")
elif [[ -n "${PRIMEAGENT_URL}" ]]; then
  PUSH_CMD+=(--target "${PRIMEAGENT_URL}")
  [[ -n "${PRIMEAGENT_API_KEY}" ]] && PUSH_CMD+=(--api-key "${PRIMEAGENT_API_KEY}")
else
  echo "ERROR: set PRIMEAGENT_ENV (Approach B) or PRIMEAGENT_URL (Approach A)" >&2
  exit 1
fi

if [[ -n "${PRIMEAGENT_PROJECT_ID}" ]]; then
  PUSH_CMD+=(--project-id "${PRIMEAGENT_PROJECT_ID}")
elif [[ -n "${PRIMEAGENT_PROJECT}" ]]; then
  PUSH_CMD+=(--project "${PRIMEAGENT_PROJECT}")
fi

[[ "${DRY_RUN}" == "true" ]] && PUSH_CMD+=(--dry-run)

# ── Push ──────────────────────────────────────────────────────────────────── #

echo "==> Pushing flows from ${FLOWS_DIR} ..."
[[ "${DRY_RUN}" == "true" ]] && echo "    (dry run — no changes will be made)"
echo "==> Running: ${PUSH_CMD[*]}"
"${PUSH_CMD[@]}"

echo "==> Done."
