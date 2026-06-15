#!/usr/bin/env bash
# Install PC Ubuntu security audit (replaces legacy system-monitor.sh).
# Run on pc-ubuntu as root:
#   sudo bash /home/octadecimal/octadecimal.pro/scripts/install-pc-ubuntu-security-audit.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
AUDIT="${REPO_ROOT}/scripts/octa-pc-ubuntu-security-audit.sh"
WATCH="${REPO_ROOT}/scripts/octa-pc-ubuntu-sudo-audit-watch.sh"
SUDOERS_SRC="${REPO_ROOT}/scripts/sudoers.d/octa-pc-ubuntu-audit"
CRON_SRC="${REPO_ROOT}/scripts/cron.d/octa-pc-ubuntu-security-audit"
DEST_AUDIT="/usr/local/bin/octa-pc-ubuntu-security-audit.sh"
DEST_WATCH="/usr/local/bin/octa-pc-ubuntu-sudo-audit-watch.sh"
LEGACY="/usr/local/bin/system-monitor.sh"
SUDO_LOG="/var/log/octa-sudo.log"

uninstall() {
  rm -f /etc/cron.d/octa-pc-ubuntu-security-audit
  rm -f "${DEST_AUDIT}" "${DEST_WATCH}"
  rm -f /usr/local/bin/system-monitor.sh
  rm -f /etc/sudoers.d/octa-pc-ubuntu-audit
  echo "Removed PC Ubuntu security audit (restore legacy from *.bak if needed)"
}

install() {
  if [[ "$(id -u)" -ne 0 ]]; then
    echo "Run as root on pc-ubuntu:" >&2
    echo "  sudo bash ${SCRIPT_DIR}/$(basename "$0")" >&2
    exit 1
  fi

  for f in "${AUDIT}" "${WATCH}" "${SUDOERS_SRC}" "${CRON_SRC}"; do
    if [[ ! -f "${f}" ]]; then
      echo "Missing required file: ${f}" >&2
      exit 1
    fi
  done

  mkdir -p /var/log/octa /var/lib/octa
  touch "${SUDO_LOG}"
  chmod 640 "${SUDO_LOG}"
  chown root:adm "${SUDO_LOG}"

  install -m 755 "${AUDIT}" "${DEST_AUDIT}"
  install -m 755 "${WATCH}" "${DEST_WATCH}"

  if [[ -f "${LEGACY}" && ! -L "${LEGACY}" ]]; then
    cp -a "${LEGACY}" "${LEGACY}.bak.$(date +%Y%m%d)"
    echo "Backed up legacy ${LEGACY}"
  fi
  ln -sf "${DEST_AUDIT}" "${LEGACY}"

  install -m 440 -o root -g root "${SUDOERS_SRC}" /etc/sudoers.d/octa-pc-ubuntu-audit
  if command -v visudo >/dev/null 2>&1; then
    if ! visudo -c -f /etc/sudoers.d/octa-pc-ubuntu-audit >/dev/null 2>&1; then
      echo "Warning: visudo check failed — verify /etc/sudoers.d/octa-pc-ubuntu-audit" >&2
    fi
  fi

  install -m 644 "${CRON_SRC}" /etc/cron.d/octa-pc-ubuntu-security-audit

  legacy_cron="$(crontab -l -u root 2>/dev/null || true)"
  if [[ -n "${legacy_cron}" ]] && grep -q system-monitor <<<"${legacy_cron}"; then
    grep -v system-monitor <<<"${legacy_cron}" | crontab -u root -
    echo "Removed legacy system-monitor from root crontab"
  fi
  rm -f /etc/cron.hourly/system-monitor /etc/cron.hourly/octa-system-monitor 2>/dev/null || true

  echo ""
  echo "Installed PC Ubuntu security audit"
  echo "  Daily:  06:00 UTC → ${DEST_AUDIT}"
  echo "  Sudo:   every 5 min → ${DEST_WATCH}"
  echo "  Legacy: ${LEGACY} → symlink to new audit"
  echo "  Mail:   security@octadecimal.pl"
  echo ""
  echo "Test:"
  echo "  ${DEST_AUDIT} --test-email"
  echo "  ${DEST_AUDIT} --report-only"
}

case "${1:-}" in
  --uninstall) uninstall ;;
  "") install ;;
  *)
    echo "Usage: sudo $0 [--uninstall]" >&2
    exit 1
    ;;
esac

echo "Runbook: docs/runbooks/pc-ubuntu-security-audit.md"
