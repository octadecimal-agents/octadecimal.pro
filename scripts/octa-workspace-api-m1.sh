#!/usr/bin/env bash
# Start Octa Workspace API on M1 (daily driver, server mode) — manual or launchd.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

export OCTA_NODE=m1
export CALENDAR_PROVIDER="${CALENDAR_PROVIDER:-auto}"
export OCTA_WORKSPACE_LOG="${OCTA_WORKSPACE_LOG:-${HOME}/.octa/logs/workspace-api-m1.log}"

exec "${REPO_ROOT}/scripts/octa-workspace-api-dev.sh" "$@"
