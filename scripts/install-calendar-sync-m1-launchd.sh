#!/usr/bin/env bash
# Install LaunchAgent: hourly calendar cache sync for M1 (ceo GUI domain).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE="${REPO_ROOT}/scripts/launchd/pl.octadecimal.calendar-sync-m1.plist.template"
LABEL="pl.octadecimal.calendar-sync-m1"
CEO_USER="${OCTA_M1_USER:-ceo}"
CEO_HOME="$(eval echo "~${CEO_USER}")"
CEO_REPO="${OCTA_M1_REPO:-${CEO_HOME}/Developer/Repositories/octadecimal-agents/octadecimal.pro}"
DEST="${CEO_HOME}/Library/LaunchAgents/pl.octadecimal.calendar-sync-m1.plist"

run_as_ceo() {
  sudo -u "${CEO_USER}" env \
    HOME="${CEO_HOME}" \
    USER="${CEO_USER}" \
    LOGNAME="${CEO_USER}" \
    PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin" \
    "$@"
}

if [[ "${1:-}" == "--uninstall" ]]; then
  uid="$(id -u "${CEO_USER}")"
  launchctl bootout "gui/${uid}/${LABEL}" 2>/dev/null || true
  rm -f "${DEST}"
  echo "Removed ${LABEL}"
  exit 0
fi

if [[ ! -f "${TEMPLATE}" ]]; then
  echo "Missing ${TEMPLATE}" >&2
  exit 1
fi

if [[ ! -d "${CEO_REPO}" ]]; then
  echo "Repo not found: ${CEO_REPO}" >&2
  exit 1
fi

chmod +x "${CEO_REPO}/scripts/octa-calendar-sync-m1.sh"
mkdir -p "${CEO_HOME}/Library/LaunchAgents" "${CEO_HOME}/.octa/logs"

sed -e "s|@REPO_ROOT@|${CEO_REPO}|g" -e "s|@HOME@|${CEO_HOME}|g" "${TEMPLATE}" >"${DEST}"
chown "${CEO_USER}:staff" "${DEST}" 2>/dev/null || true

uid="$(id -u "${CEO_USER}")"
if ! launchctl print "gui/${uid}" >/dev/null 2>&1; then
  echo "WARNING: gui/${uid} unavailable — sync runs after ceo logs in at console." >&2
  echo "Plist installed: ${DEST}" >&2
  exit 0
fi

launchctl bootout "gui/${uid}/${LABEL}" 2>/dev/null || true
launchctl bootstrap "gui/${uid}" "${DEST}"
launchctl enable "gui/${uid}/${LABEL}"
launchctl kickstart -k "gui/${uid}/${LABEL}" 2>/dev/null || true

echo "Installed calendar sync LaunchAgent for ${CEO_USER}"
echo "  Label: ${LABEL}"
echo "  Log:   ${CEO_HOME}/.octa/logs/calendar-sync-m1.log"
