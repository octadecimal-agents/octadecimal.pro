#!/usr/bin/env bash
# Install daily M1 smoke check on M5 (user crontab, 09:00 local).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CRON_TAG="# octa-m5-m1-smoke-daily"
CRON_LINE="0 9 * * * cd ${REPO_ROOT} && OCTA_SMOKE_UPDATE_DOC=1 ./scripts/octa-m1-smoke-daily.sh >> ${HOME}/.octa/logs/m5-6-smoke-cron.log 2>&1 ${CRON_TAG}"

usage() {
  cat <<EOF
Usage: $(basename "$0") [--uninstall]

Installs user crontab entry: daily 09:00 smoke M1 from M5, append logs, refresh smoke-log.md table.
Requires: ssh m1-ceo (BatchMode) working from this Mac.
EOF
}

if [[ "${1:-}" == "--uninstall" ]]; then
  tmp="$(mktemp)"
  crontab -l 2>/dev/null | grep -v "${CRON_TAG}" >"${tmp}" || true
  crontab "${tmp}" || true
  rm -f "${tmp}"
  echo "Removed ${CRON_TAG} from crontab"
  exit 0
fi

if ! ssh -o BatchMode=yes -o ConnectTimeout=5 "${OCTA_M1_SSH_HOST:-m1-ceo}" true 2>/dev/null; then
  echo "SSH to ${OCTA_M1_SSH_HOST:-m1-ceo} not available — fix ~/.ssh/config first" >&2
  exit 1
fi

mkdir -p "${HOME}/.octa/logs"
chmod +x "${REPO_ROOT}/scripts/octa-m1-smoke-daily.sh"

tmp="$(mktemp)"
( crontab -l 2>/dev/null | grep -v "${CRON_TAG}" || true
  echo "${CRON_LINE}"
) >"${tmp}"
crontab "${tmp}"
rm -f "${tmp}"

echo "Installed daily M1 smoke at 09:00"
echo "  Log: ~/.octa/logs/m5-6-m1-smoke.log"
echo "  Cron log: ~/.octa/logs/m5-6-smoke-cron.log"
echo "  Uninstall: $0 --uninstall"
