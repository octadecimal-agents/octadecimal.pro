#!/usr/bin/env bash
# Incremental Knowledge embed sync for dev Qdrant (:6335, knowledge_chunks_dev only).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

export PATH="${PATH:-/usr/bin:/bin}:/opt/homebrew/bin:/usr/local/bin:${HOME}/.local/bin"

OCTA_STATE="${OCTA_STATE_DIR:-${HOME}/.octa}"
LOG_FILE="${OCTA_SYNC_LOG:-${OCTA_STATE}/logs/embed-sync.log}"
LOG_DIR="$(dirname "${LOG_FILE}")"
mkdir -p "${LOG_DIR}"

log() {
  printf '[%s] %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$*" >>"$LOG_FILE"
}

export KNOWLEDGE_ROOT="${KNOWLEDGE_ROOT:-${HOME}/Developer/Knowledge}"
export QDRANT_URL="${QDRANT_URL:-http://127.0.0.1:6335}"
export QDRANT_COLLECTION="${QDRANT_COLLECTION:-knowledge_chunks_dev}"

if [[ "${QDRANT_COLLECTION}" != "knowledge_chunks_dev" ]]; then
  log "ERROR: refusing sync — QDRANT_COLLECTION must be knowledge_chunks_dev (got: ${QDRANT_COLLECTION})"
  exit 1
fi

case "${QDRANT_URL}" in
  http://127.0.0.1:6335 | http://127.0.0.1:6335/* | http://localhost:6335 | http://localhost:6335/*) ;;
  *)
    log "ERROR: refusing sync — QDRANT_URL must be local dev :6335 (got: ${QDRANT_URL})"
    exit 1
    ;;
esac

if ! command -v uv >/dev/null 2>&1; then
  log "ERROR: uv not found in PATH (${PATH})"
  exit 1
fi

log "starting embed sync dev (knowledge_root=${KNOWLEDGE_ROOT})"

if [[ "${OCTA_SYNC_SKIP_QDRANT:-0}" != "1" ]]; then
  if ! curl -sf "${QDRANT_URL}/collections" >/dev/null 2>&1; then
    log "Qdrant not reachable at ${QDRANT_URL} — starting via octa-qdrant-dev.sh"
    if ! ./scripts/octa-qdrant-dev.sh >>"$LOG_FILE" 2>&1; then
      log "ERROR: failed to start Qdrant dev"
      exit 1
    fi
  fi
fi

sync_args=(sync --dev)
if [[ "${OCTA_SYNC_DRY_RUN:-0}" == "1" ]]; then
  sync_args+=(--dry-run)
fi

log "running: uv run python scripts/embed-knowledge.py ${sync_args[*]}"
if output="$(uv run python scripts/embed-knowledge.py "${sync_args[@]}" 2>&1)"; then
  while IFS= read -r line; do
    log "$line"
  done <<<"$output"
  log "sync complete"
else
  log "ERROR: sync failed"
  while IFS= read -r line; do
    log "$line"
  done <<<"$output"
  exit 1
fi
