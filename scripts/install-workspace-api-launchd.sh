#!/usr/bin/env bash
# Install macOS launchd agent: Octa Workspace API on localhost:8042.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE="${REPO_ROOT}/scripts/launchd/pl.octadecimal.workspace-api-dev.plist.template"
DEST="${HOME}/Library/LaunchAgents/pl.octadecimal.workspace-api-dev.plist"
LABEL="pl.octadecimal.workspace-api-dev"
UID="$(id -u)"

if [[ ! -f "${TEMPLATE}" ]]; then
  echo "Missing template: ${TEMPLATE}" >&2
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

launchctl bootout "gui/${UID}/${LABEL}" 2>/dev/null || true
launchctl bootstrap "gui/${UID}" "${DEST}"
launchctl enable "gui/${UID}/${LABEL}"
launchctl kickstart -k "gui/${UID}/${LABEL}"

echo "Installed ${DEST}"
echo "  Label:    ${LABEL}"
echo "  URL:      http://127.0.0.1:8042/"
echo "  Log:      ${HOME}/.octa/logs/workspace-api.log"
echo ""
echo "Verify:"
echo "  curl -s http://127.0.0.1:8042/workspace/health | python3 -m json.tool"
echo ""
echo "Manual restart:"
echo "  launchctl kickstart -k gui/${UID}/${LABEL}"
echo ""
echo "Uninstall:"
echo "  launchctl bootout gui/${UID}/${LABEL} && rm ${DEST}"
