#!/usr/bin/env bash
# Rsync Knowledge from M5 (SSOT) → M1 ceo. Safe defaults: no --delete, no .secrets.
set -euo pipefail

export PATH="${PATH:-/usr/bin:/bin}:/opt/homebrew/bin:/usr/local/bin:${HOME}/.local/bin"

KNOWLEDGE_ROOT="${KNOWLEDGE_ROOT:-${HOME}/Developer/Knowledge}"
M1_SSH_HOST="${M1_SSH_HOST:-m1-ceo}"
M1_KNOWLEDGE_DEST="${M1_KNOWLEDGE_DEST:-Developer/Knowledge}"
OCTA_STATE="${OCTA_STATE_DIR:-${HOME}/.octa}"
LOG_FILE="${OCTA_KNOWLEDGE_M1_LOG:-${OCTA_STATE}/logs/knowledge-sync-m1.log}"
LOCK_DIR="${OCTA_STATE}/locks/knowledge-sync-m1"
RSYNC_DRY_RUN="${OCTA_KNOWLEDGE_M1_DRY_RUN:-0}"
RSYNC_MIRROR="${OCTA_KNOWLEDGE_M1_MIRROR:-0}"

log() {
  mkdir -p "$(dirname "${LOG_FILE}")"
  printf '[%s] %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$*" >>"${LOG_FILE}"
}

fail() {
  log "ERROR: $*"
  exit 1
}

if [[ ! -d "${KNOWLEDGE_ROOT}" ]]; then
  fail "KNOWLEDGE_ROOT not found: ${KNOWLEDGE_ROOT}"
fi

if ! command -v rsync >/dev/null 2>&1; then
  fail "rsync not found"
fi

if ! ssh -o BatchMode=yes -o ConnectTimeout=15 "${M1_SSH_HOST}" 'test -d "${HOME}"' 2>/dev/null; then
  fail "SSH to ${M1_SSH_HOST} failed (load key: ssh-add ~/.ssh/m1_ceo_ed25519)"
fi

mkdir -p "${LOCK_DIR}"
if ! mkdir "${LOCK_DIR}/.lock" 2>/dev/null; then
  log "skip — another sync in progress"
  exit 0
fi
trap 'rmdir "${LOCK_DIR}/.lock" 2>/dev/null || true' EXIT

rsync_args=(
  -az
  --exclude '.knowledge-index/'
  --exclude '.secrets/'
  --exclude '.git/'
  --exclude '__pycache__/'
  --exclude '.DS_Store'
  --exclude '.cursor/'
  --exclude 'node_modules/'
)

if [[ "${RSYNC_DRY_RUN}" == "1" ]]; then
  rsync_args+=(--dry-run -v)
fi

if [[ "${RSYNC_MIRROR}" == "1" ]]; then
  rsync_args+=(--delete)
fi

log "start → ${M1_SSH_HOST}:${M1_KNOWLEDGE_DEST} (mirror=${RSYNC_MIRROR} dry_run=${RSYNC_DRY_RUN})"

if rsync "${rsync_args[@]}" \
  "${KNOWLEDGE_ROOT}/" \
  "${M1_SSH_HOST}:${M1_KNOWLEDGE_DEST}/" >>"${LOG_FILE}" 2>&1; then
  log "complete"
else
  fail "rsync failed — see log above"
fi

# Optional: touch marker on M1 for ops
ssh -o BatchMode=yes -o ConnectTimeout=15 "${M1_SSH_HOST}" \
  "mkdir -p ${M1_KNOWLEDGE_DEST}/.octa-sync && date -u '+%Y-%m-%dT%H:%M:%SZ' > ${M1_KNOWLEDGE_DEST}/.octa-sync/last-rsync-from-m5.txt" \
  >>"${LOG_FILE}" 2>&1 || log "warn: could not write M1 sync marker"
