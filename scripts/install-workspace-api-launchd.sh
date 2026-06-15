#!/usr/bin/env bash
# Install macOS launchd agent: Octa Workspace API on M5 (dev node, localhost:8042).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE="${REPO_ROOT}/scripts/launchd/pl.octadecimal.workspace-api-dev.plist.template"
DEST="${HOME}/Library/LaunchAgents/pl.octadecimal.workspace-api-dev.plist"
LABEL="pl.octadecimal.workspace-api-dev"
M1_LABEL="pl.octadecimal.workspace-api-m1"
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

if launchctl print "gui/${GUI_UID}/${M1_LABEL}" >/dev/null 2>&1; then
  echo "WARNING: ${M1_LABEL} is loaded (M1 server mode)." >&2
  echo "  Only one Workspace agent should bind :8042. Uninstall M1 first:" >&2
  echo "    ./scripts/install-workspace-api-m1-launchd.sh --uninstall" >&2
  exit 1
fi

mkdir -p "${HOME}/Library/LaunchAgents" "${HOME}/.octa/logs"

echo "Syncing dependencies..."
(cd "${REPO_ROOT}" && uv sync)

echo "Seeding demo data (one-time before launchd)..."
OCTA_WORKSPACE_SKIP_UV_SYNC=1 "${REPO_ROOT}/scripts/octa-workspace-api-dev.sh" --seed-only

if curl -sf "http://127.0.0.1:8042/workspace/health" >/dev/null 2>&1; then
  echo "WARNING: something already listens on :8042 — stop ./scripts/octa-mvp-up.sh before installing launchd" >&2
  exit 1
fi

sed -e "s|@REPO_ROOT@|${REPO_ROOT}|g" -e "s|@HOME@|${HOME}|g" "${TEMPLATE}" >"${DEST}"

launchctl bootout "gui/${GUI_UID}/${LABEL}" 2>/dev/null || true
launchctl bootstrap "gui/${GUI_UID}" "${DEST}"
launchctl enable "gui/${GUI_UID}/${LABEL}"
launchctl kickstart -k "gui/${GUI_UID}/${LABEL}"

echo "Installed ${DEST}"
echo "  Label:    ${LABEL}"
echo "  URL:      http://127.0.0.1:8042/"
echo "  Log:      ${HOME}/.octa/logs/workspace-api.log"
echo ""
echo "Verify:"
echo "  curl -s http://127.0.0.1:8042/workspace/health | python3 -m json.tool"
echo ""
echo "Manual restart:"
echo "  launchctl kickstart -k gui/${GUI_UID}/${LABEL}"
echo ""
echo "Uninstall:"
echo "  ./scripts/install-workspace-api-launchd.sh --uninstall"
echo ""
echo "M1 server mode (daily driver): docs/runbooks/workspace-m1-server-mode.md"
