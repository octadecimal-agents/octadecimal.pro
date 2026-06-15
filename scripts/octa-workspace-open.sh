#!/usr/bin/env bash
# M5.6.4 — open Workspace UI on localhost; kickstart launchd if API is down.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOST="${WORKSPACE_HOST:-127.0.0.1}"
PORT="${WORKSPACE_PORT:-8042}"
BASE_URL="http://${HOST}:${PORT}"
HEALTH_URL="${BASE_URL}/workspace/health"
DAEMON_LABEL="pl.octadecimal.workspace-api-m1-server"
AGENT_LABEL="pl.octadecimal.workspace-api-m1"
KICKSTART="${OCTA_WORKSPACE_OPEN_KICKSTART:-1}"

health_ok() {
  curl -sf "${HEALTH_URL}" >/dev/null 2>&1
}

kickstart_launchd() {
  if launchctl print "system/${DAEMON_LABEL}" >/dev/null 2>&1; then
    echo "Kickstarting LaunchDaemon ${DAEMON_LABEL}..."
    if [[ "$(id -u)" -eq 0 ]]; then
      launchctl kickstart -k "system/${DAEMON_LABEL}"
    else
      sudo launchctl kickstart -k "system/${DAEMON_LABEL}"
    fi
    return 0
  fi
  local uid
  uid="$(id -u)"
  if launchctl print "gui/${uid}/${AGENT_LABEL}" >/dev/null 2>&1; then
    echo "Kickstarting LaunchAgent ${AGENT_LABEL}..."
    launchctl kickstart -k "gui/${uid}/${AGENT_LABEL}"
    return 0
  fi
  echo "No M1 launchd job found — start manually:" >&2
  echo "  sudo ${REPO_ROOT}/scripts/install-workspace-api-m1-launchd.sh --daemon" >&2
  echo "  or: ${REPO_ROOT}/scripts/octa-mvp-up.sh (M5 dev only)" >&2
  return 1
}

wait_for_health() {
  local tries="${1:-15}"
  local i
  for ((i = 1; i <= tries; i++)); do
    if health_ok; then
      return 0
    fi
    sleep 1
  done
  return 1
}

if ! health_ok; then
  echo "Workspace not responding at ${HEALTH_URL}"
  if [[ "${KICKSTART}" == "1" ]]; then
    kickstart_launchd || true
    if ! wait_for_health 20; then
      echo "Health check still failing after kickstart." >&2
      echo "Logs: tail -f ~/.octa/logs/workspace-api-m1.log" >&2
      exit 1
    fi
  else
    echo "Set OCTA_WORKSPACE_OPEN_KICKSTART=1 to auto-restart launchd." >&2
    exit 1
  fi
fi

if health_ok; then
  python3 - <<PY 2>/dev/null || true
import json, urllib.request
h = json.load(urllib.request.urlopen("${HEALTH_URL}"))
print(f"Workspace {h.get('status')} · calendar={h.get('calendar_source')} · review_pending={h.get('review_pending_count')}")
PY
fi

if [[ "$(uname -s)" == "Darwin" ]]; then
  open "${BASE_URL}/"
else
  echo "Open in browser: ${BASE_URL}/"
fi
