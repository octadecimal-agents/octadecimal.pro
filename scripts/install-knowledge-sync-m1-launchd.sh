#!/usr/bin/env bash
# Install launchd agent: rsync Knowledge M5 → M1 on change (WatchPaths) + at login.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE="${REPO_ROOT}/scripts/launchd/pl.octadecimal.knowledge-sync-m1.plist.template"
DEST="${HOME}/Library/LaunchAgents/pl.octadecimal.knowledge-sync-m1.plist"
LABEL="pl.octadecimal.knowledge-sync-m1"
GUI_UID="$(id -u)"
KNOWLEDGE_ROOT="${KNOWLEDGE_ROOT:-${HOME}/Developer/Knowledge}"

if [[ "${1:-}" == "--uninstall" ]]; then
  launchctl bootout "gui/${GUI_UID}/${LABEL}" 2>/dev/null || true
  rm -f "${DEST}"
  echo "Removed ${LABEL}"
  exit 0
fi

if [[ ! -f "${TEMPLATE}" ]]; then
  echo "Missing template: ${TEMPLATE}" >&2
  exit 1
fi

if [[ ! -d "${KNOWLEDGE_ROOT}" ]]; then
  echo "KNOWLEDGE_ROOT not found: ${KNOWLEDGE_ROOT}" >&2
  exit 1
fi

chmod +x "${REPO_ROOT}/scripts/octa-knowledge-sync-m1.sh"
mkdir -p "${HOME}/Library/LaunchAgents" "${HOME}/.octa/logs"

sed -e "s|@REPO_ROOT@|${REPO_ROOT}|g" \
    -e "s|@HOME@|${HOME}|g" \
    -e "s|@KNOWLEDGE_ROOT@|${KNOWLEDGE_ROOT}|g" \
    "${TEMPLATE}" >"${DEST}"

launchctl bootout "gui/${GUI_UID}/${LABEL}" 2>/dev/null || true
launchctl bootstrap "gui/${GUI_UID}" "${DEST}"
launchctl enable "gui/${GUI_UID}/${LABEL}"
launchctl kickstart -k "gui/${GUI_UID}/${LABEL}" 2>/dev/null || true

echo "Installed ${DEST}"
echo "  Label:       ${LABEL}"
echo "  WatchPaths:  ${KNOWLEDGE_ROOT}"
echo "  Throttle:    120s between runs"
echo "  Log:         ${HOME}/.octa/logs/knowledge-sync-m1.log"
echo ""
echo "Manual sync:"
echo "  ${REPO_ROOT}/scripts/octa-knowledge-sync-m1.sh"
echo ""
echo "Manual trigger:"
echo "  launchctl kickstart -k gui/${GUI_UID}/${LABEL}"
echo ""
echo "Uninstall:"
echo "  $0 --uninstall"
