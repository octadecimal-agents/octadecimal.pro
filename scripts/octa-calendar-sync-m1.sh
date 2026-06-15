#!/usr/bin/env bash
# M1 — refresh ~/.octa/calendar-cache.json from EventKit (LaunchAgent / manual).
# Workspace LaunchDaemon uses CALENDAR_PROVIDER=cache and reads this file only.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${REPO_ROOT}"

export WORKSPACE_ENABLED=1
export KNOWLEDGE_ROOT="${KNOWLEDGE_ROOT:-${HOME}/Developer/Knowledge}"
export CALENDAR_PROVIDER=macos
export OCTA_STATE_DIR="${OCTA_STATE_DIR:-${HOME}/.octa}"
LOG="${OCTA_CALENDAR_SYNC_LOG:-${OCTA_STATE_DIR}/logs/calendar-sync-m1.log}"
mkdir -p "$(dirname "${LOG}")"

log() {
  printf '[%s] %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$*" >>"${LOG}"
}

if [[ "$(uname -s)" != "Darwin" ]]; then
  log "skip — not macOS"
  exit 0
fi

log "calendar sync start"

set +e
RESULT="$(uv run python - <<'PY' 2>&1
import asyncio
import os
import sys

os.environ["CALENDAR_PROVIDER"] = "macos"

from secure_agentic_ai.infrastructure.workspace.config import WorkspaceConfig
from secure_agentic_ai.infrastructure.macos.calendar_provider import list_today_calendar_events

async def main() -> int:
    config = WorkspaceConfig.from_env()
    events, source = await list_today_calendar_events(config)
    print(f"source={source} events={len(events)}")
    return 0 if source == "macos" else 1

sys.exit(asyncio.run(main()))
PY
)"
RC=$?
set -e

log "${RESULT}"
echo "${RESULT}"

if [[ "${RC}" -eq 0 ]]; then
  exit 0
fi

echo "Calendar sync failed — run: sudo ${REPO_ROOT}/scripts/install-m1-calendar-automation.sh" >&2
exit 1
