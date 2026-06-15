#!/usr/bin/env bash
# Trigger PC Ubuntu audit when /var/log/octa-sudo.log grows (sudo usage).
set -euo pipefail

SUDO_LOG="${OCTA_PC_SUDO_LOG:-/var/log/octa-sudo.log}"
STATE_DIR="${OCTA_PC_AUDIT_STATE_DIR:-/var/lib/octa}"
OFFSET_FILE="${STATE_DIR}/pc-ubuntu-sudo.offset"
AUDIT_SCRIPT="${OCTA_PC_AUDIT_SCRIPT:-/usr/local/bin/octa-pc-ubuntu-security-audit.sh}"
THROTTLE_SEC="${OCTA_PC_SUDO_AUDIT_THROTTLE:-300}"
LAST_RUN_FILE="${STATE_DIR}/pc-ubuntu-sudo.last-run"

mkdir -p "${STATE_DIR}"

[[ -f "${SUDO_LOG}" ]] || exit 0
[[ -x "${AUDIT_SCRIPT}" ]] || exit 0

current_lines="$(wc -l < "${SUDO_LOG}" | tr -d ' ')"
last_lines=0
[[ -f "${OFFSET_FILE}" ]] && last_lines="$(cat "${OFFSET_FILE}")"

if [[ "${current_lines}" -le "${last_lines}" ]]; then
  exit 0
fi

if [[ -f "${LAST_RUN_FILE}" ]]; then
  last_run="$(cat "${LAST_RUN_FILE}")"
  now="$(date +%s)"
  if (( now - last_run < THROTTLE_SEC )); then
    echo "${current_lines}" > "${OFFSET_FILE}"
    exit 0
  fi
fi

export OCTA_PC_AUDIT_TRIGGER=sudo
"${AUDIT_SCRIPT}"

echo "${current_lines}" > "${OFFSET_FILE}"
date +%s > "${LAST_RUN_FILE}"
