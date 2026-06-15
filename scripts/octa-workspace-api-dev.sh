#!/usr/bin/env bash
# Start Octa Workspace API for dev (localhost) — manual or launchd.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

export PATH="${PATH:-/usr/bin:/bin}:/opt/homebrew/bin:/usr/local/bin:${HOME}/.local/bin"

# shellcheck source=scripts/octa-workspace-env.sh
source "${REPO_ROOT}/scripts/octa-workspace-env.sh"

OCTA_STATE="${OCTA_STATE_DIR:-${HOME}/.octa}"
LOG_FILE="${OCTA_WORKSPACE_LOG:-${OCTA_STATE}/logs/workspace-api.log}"
LOG_DIR="$(dirname "${LOG_FILE}")"
mkdir -p "${LOG_DIR}"

log() {
  printf '[%s] %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$*" >>"$LOG_FILE"
}

FOREGROUND=0
SEED_ONLY=0
for arg in "$@"; do
  case "$arg" in
    --foreground) FOREGROUND=1 ;;
    --seed-only) SEED_ONLY=1 ;;
  esac
done

if [[ "${WORKSPACE_HOST}" != "127.0.0.1" && "${WORKSPACE_HOST}" != "localhost" ]]; then
  log "ERROR: refusing start — WORKSPACE_HOST must be localhost (got: ${WORKSPACE_HOST})"
  exit 1
fi

if [[ "${WORKSPACE_PORT}" != "8042" ]]; then
  log "ERROR: refusing start — WORKSPACE_PORT must be 8042 for dev (got: ${WORKSPACE_PORT})"
  exit 1
fi

if [[ "${RAG_BACKEND}" == "qdrant" && "${OCTA_WORKSPACE_SKIP_QDRANT:-0}" != "1" ]]; then
  log "RAG_BACKEND=qdrant — ensuring Qdrant dev on ${QDRANT_URL}"
  if ! ./scripts/octa-qdrant-dev.sh >>"$LOG_FILE" 2>&1; then
    log "ERROR: failed to start Qdrant dev"
    exit 1
  fi
fi

if [[ "${OCTA_WORKSPACE_SKIP_UV_SYNC:-0}" != "1" ]]; then
  log "running uv sync"
  if ! uv sync >>"$LOG_FILE" 2>&1; then
    log "ERROR: uv sync failed"
    exit 1
  fi
fi

run_seed() {
  log "seeding demo approvals"
  uv run python scripts/seed_demo.py >>"$LOG_FILE" 2>&1
  log "seeding workspace plan"
  uv run python scripts/seed_workspace_mvp.py >>"$LOG_FILE" 2>&1
}

if [[ "${OCTA_WORKSPACE_SKIP_SEED:-0}" != "1" ]]; then
  run_seed
fi

if [[ "${SEED_ONLY}" -eq 1 ]]; then
  log "seed-only complete"
  exit 0
fi

if command -v curl >/dev/null 2>&1; then
  if curl -sf "http://${WORKSPACE_HOST}:${WORKSPACE_PORT}/workspace/health" >/dev/null 2>&1; then
    log "ERROR: port ${WORKSPACE_PORT} already serving /workspace/health — stop other instance first"
    exit 1
  fi
fi

log "starting uvicorn on ${WORKSPACE_HOST}:${WORKSPACE_PORT} (node=${OCTA_NODE:-dev}, llm=${LLM_PROVIDER}, rag=${RAG_BACKEND}, calendar=${CALENDAR_PROVIDER:-auto})"

if [[ "${FOREGROUND}" -eq 1 ]]; then
  exec uv run uvicorn secure_agentic_ai.adapters.api.app:app \
    --host "${WORKSPACE_HOST}" --port "${WORKSPACE_PORT}"
fi

exec uv run uvicorn secure_agentic_ai.adapters.api.app:app \
  --host "${WORKSPACE_HOST}" --port "${WORKSPACE_PORT}" >>"$LOG_FILE" 2>&1
