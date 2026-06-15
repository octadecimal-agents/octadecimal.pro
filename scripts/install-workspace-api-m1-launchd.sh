#!/usr/bin/env bash
# Install macOS launchd agent: Octa Workspace API on M1 (server mode, localhost:8042).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE="${REPO_ROOT}/scripts/launchd/pl.octadecimal.workspace-api-m1.plist.template"
DEST="${HOME}/Library/LaunchAgents/pl.octadecimal.workspace-api-m1.plist"
LABEL="pl.octadecimal.workspace-api-m1"
DEV_LABEL="pl.octadecimal.workspace-api-dev"
GUI_UID="$(id -u)"

if [[ "${1:-}" == "--uninstall" ]]; then
  launchctl bootout "gui/${GUI_UID}/${LABEL}" 2>/dev/null || true
  rm -f "${DEST}"
  echo "Uninstalled ${LABEL}"
  exit 0
fi

if [[ ! -f "${TEMPLATE}" ]]; then
  echo "Missing template: ${TEMPLATE}" >&2
  exit 1
fi

if launchctl print "gui/${GUI_UID}/${DEV_LABEL}" >/dev/null 2>&1; then
  echo "WARNING: ${DEV_LABEL} is loaded (M5 dev launchd)." >&2
  echo "  Only one Workspace agent should bind :8042. Uninstall dev first:" >&2
  echo "    ./scripts/install-workspace-api-launchd.sh --uninstall" >&2
  echo "  Or stop dev manually before continuing." >&2
  exit 1
fi

mkdir -p "${HOME}/Library/LaunchAgents" "${HOME}/.octa/logs"

echo "Syncing dependencies..."
(cd "${REPO_ROOT}" && uv sync)

echo "Seeding demo data (one-time before launchd)..."
OCTA_WORKSPACE_SKIP_UV_SYNC=1 "${REPO_ROOT}/scripts/octa-workspace-api-m1.sh" --seed-only

if curl -sf "http://127.0.0.1:8042/workspace/health" >/dev/null 2>&1; then
  echo "ERROR: something already listens on :8042 — stop ./scripts/octa-mvp-up.sh or other instance first" >&2
  exit 1
fi

sed -e "s|@REPO_ROOT@|${REPO_ROOT}|g" -e "s|@HOME@|${HOME}|g" "${TEMPLATE}" >"${DEST}"

if ! launchctl print "gui/${GUI_UID}" >/dev/null 2>&1; then
  echo ""
  echo "Plist installed: ${DEST}"
  echo "WARNING: gui/${GUI_UID} is unavailable — user $(whoami) has no active GUI session."
  echo "  LaunchAgents start after a console login on M1."
  echo "  Next steps:"
  echo "    1. Log in at the Mac as $(whoami) (or run install from the console user account)."
  echo "    2. launchctl bootstrap gui/${GUI_UID} ${DEST}"
  echo "    3. launchctl enable gui/${GUI_UID}/${LABEL}"
  echo "    4. launchctl kickstart -k gui/${GUI_UID}/${LABEL}"
  echo ""
  echo "  Interim (SSH): OCTA_WORKSPACE_SKIP_SEED=1 OCTA_WORKSPACE_SKIP_UV_SYNC=1 \\"
  echo "    nohup ${REPO_ROOT}/scripts/octa-workspace-api-m1.sh >>${HOME}/.octa/logs/workspace-api-m1.log 2>&1 &"
  exit 0
fi

launchctl bootout "gui/${GUI_UID}/${LABEL}" 2>/dev/null || true
launchctl bootstrap "gui/${GUI_UID}" "${DEST}"
launchctl enable "gui/${GUI_UID}/${LABEL}"
launchctl kickstart -k "gui/${GUI_UID}/${LABEL}"

echo ""
echo "Installed M1 server mode: ${DEST}"
echo "  Label:    ${LABEL}"
echo "  URL:      http://127.0.0.1:8042/"
echo "  Log:      ${HOME}/.octa/logs/workspace-api-m1.log"
echo "  Runbook:  docs/runbooks/workspace-m1-server-mode.md"
echo ""
echo "Verify:"
echo "  curl -s http://127.0.0.1:8042/workspace/health | python3 -m json.tool"
echo ""
echo "Manual restart:"
echo "  launchctl kickstart -k gui/${GUI_UID}/${LABEL}"
echo ""
echo "Uninstall:"
echo "  ./scripts/install-workspace-api-m1-launchd.sh --uninstall"
