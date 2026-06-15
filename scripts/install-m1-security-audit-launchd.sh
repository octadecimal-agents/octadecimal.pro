#!/usr/bin/env bash
# Install M1 security audit: sudo log + daily email + sudo-triggered email.
# Run on M1 as admin: sudo ./scripts/install-m1-security-audit-launchd.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
AUDIT_SCRIPT="${REPO_ROOT}/scripts/octa-m1-security-audit.sh"
SUDOERS_SRC="${REPO_ROOT}/scripts/sudoers.d/octa-m1-audit"
DAILY_TEMPLATE="${REPO_ROOT}/scripts/launchd/pl.octadecimal.m1-security-audit-daily.plist.template"
WATCH_TEMPLATE="${REPO_ROOT}/scripts/launchd/pl.octadecimal.m1-sudo-audit-watch.plist.template"
DAILY_LABEL="pl.octadecimal.m1-security-audit-daily"
WATCH_LABEL="pl.octadecimal.m1-sudo-audit-watch"
CEO_USER="${OCTA_M1_USER:-ceo}"
CEO_HOME="${OCTA_M1_CEO_HOME:-/Users/${CEO_USER}}"
CEO_REPO="${OCTA_M1_REPO:-${CEO_HOME}/Developer/Repositories/octadecimal-agents/octadecimal.pro}"
SUDO_LOG="/var/log/octa-sudo.log"

uninstall() {
  launchctl bootout "system/${DAILY_LABEL}" 2>/dev/null || true
  launchctl bootout "system/${WATCH_LABEL}" 2>/dev/null || true
  rm -f "/Library/LaunchDaemons/pl.octadecimal.m1-security-audit-daily.plist"
  rm -f "/Library/LaunchDaemons/pl.octadecimal.m1-sudo-audit-watch.plist"
  rm -f "/etc/sudoers.d/octa-m1-audit"
  echo "Removed audit LaunchDaemons and sudoers drop-in (sudo log file kept: ${SUDO_LOG})"
}

install() {
  if [[ "$(id -u)" -ne 0 ]]; then
    echo "Run as root on M1:" >&2
    echo "  sudo OCTA_M1_REPO=${CEO_REPO} $0" >&2
    exit 1
  fi
  if [[ ! -x "${AUDIT_SCRIPT}" ]]; then
    chmod +x "${AUDIT_SCRIPT}"
  fi
  if [[ ! -f "${SUDOERS_SRC}" ]]; then
    echo "Missing ${SUDOERS_SRC}" >&2
    exit 1
  fi

  mkdir -p /var/log/octa
  touch "${SUDO_LOG}"
  chmod 640 "${SUDO_LOG}"
  chown root:wheel "${SUDO_LOG}"

  install -m 440 -o root -g wheel "${SUDOERS_SRC}" /etc/sudoers.d/octa-m1-audit
  if ! visudo -c -f /etc/sudoers.d/octa-m1-audit >/dev/null; then
    rm -f /etc/sudoers.d/octa-m1-audit
    echo "Invalid sudoers drop-in — aborted" >&2
    exit 1
  fi

  sed -e "s|@REPO_ROOT@|${CEO_REPO}|g" -e "s|@CEO_HOME@|${CEO_HOME}|g" \
    "${DAILY_TEMPLATE}" >"/Library/LaunchDaemons/pl.octadecimal.m1-security-audit-daily.plist"
  sed -e "s|@REPO_ROOT@|${CEO_REPO}|g" -e "s|@CEO_HOME@|${CEO_HOME}|g" \
    "${WATCH_TEMPLATE}" >"/Library/LaunchDaemons/pl.octadecimal.m1-sudo-audit-watch.plist"
  chmod 644 /Library/LaunchDaemons/pl.octadecimal.m1-security-audit-*.plist
  chown root:wheel /Library/LaunchDaemons/pl.octadecimal.m1-security-audit-*.plist

  launchctl bootout "system/${DAILY_LABEL}" 2>/dev/null || true
  launchctl bootout "system/${WATCH_LABEL}" 2>/dev/null || true
  launchctl bootstrap system "/Library/LaunchDaemons/pl.octadecimal.m1-security-audit-daily.plist"
  launchctl bootstrap system "/Library/LaunchDaemons/pl.octadecimal.m1-sudo-audit-watch.plist"
  launchctl enable "system/${DAILY_LABEL}"
  launchctl enable "system/${WATCH_LABEL}"

  echo ""
  echo "Installed M1 security audit"
  echo "  Daily:     06:00 local → ${DAILY_LABEL}"
  echo "  Sudo:      WatchPaths ${SUDO_LOG} → ${WATCH_LABEL} (throttle 300s)"
  echo "  Mail to:   security@octadecimal.pl"
  echo "  Mail from: admin@octadecimal.pl (sendmail)"
  echo "  Reports:   /var/log/octa/m1-audit-reports/"
  echo ""
  echo "Test:"
  echo "  ${AUDIT_SCRIPT} --test-email"
  echo "  ${AUDIT_SCRIPT} --report-only"
}

case "${1:-}" in
  --uninstall) uninstall ;;
  "") install ;;
  *)
    echo "Usage: sudo $0 [--uninstall]" >&2
    exit 1
    ;;
esac

echo ""
echo "Runbook: docs/runbooks/m1-security-audit.md"
