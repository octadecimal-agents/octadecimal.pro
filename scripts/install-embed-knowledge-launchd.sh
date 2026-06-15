#!/usr/bin/env bash
# Install macOS launchd agent: Knowledge embed sync every 6h (dev Qdrant only).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE="${REPO_ROOT}/scripts/launchd/pl.octadecimal.embed-knowledge-dev.plist.template"
DEST="${HOME}/Library/LaunchAgents/pl.octadecimal.embed-knowledge-dev.plist"
LABEL="pl.octadecimal.embed-knowledge-dev"
UID="$(id -u)"

if [[ ! -f "${TEMPLATE}" ]]; then
  echo "Missing template: ${TEMPLATE}" >&2
  exit 1
fi

mkdir -p "${HOME}/Library/LaunchAgents" "${HOME}/.octa/logs"
sed -e "s|@REPO_ROOT@|${REPO_ROOT}|g" -e "s|@HOME@|${HOME}|g" "${TEMPLATE}" >"${DEST}"

launchctl bootout "gui/${UID}/${LABEL}" 2>/dev/null || true
launchctl bootstrap "gui/${UID}" "${DEST}"
launchctl enable "gui/${UID}/${LABEL}"

echo "Installed ${DEST}"
echo "  Label:    ${LABEL}"
echo "  Interval: every 6 hours (+ RunAtLoad)"
echo "  Log:      ${HOME}/.octa/logs/embed-sync.log"
echo ""
echo "Manual trigger:"
echo "  launchctl kickstart -k gui/${UID}/${LABEL}"
echo ""
echo "Uninstall:"
echo "  launchctl bootout gui/${UID}/${LABEL} && rm ${DEST}"
