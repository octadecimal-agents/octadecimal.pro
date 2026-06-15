#!/usr/bin/env bash
# M1 security audit — collect host state and email security@octadecimal.pl.
# Triggers: daily (launchd), sudo (WatchPaths on /var/log/octa-sudo.log), manual.
set -euo pipefail

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

TRIGGER="${OCTA_M1_AUDIT_TRIGGER:-manual}"
MAIL_TO="${OCTA_M1_AUDIT_MAIL_TO:-security@octadecimal.pl}"
MAIL_FROM="${OCTA_M1_AUDIT_MAIL_FROM:-admin@octadecimal.pl}"
MAIL_FROM_NAME="${OCTA_M1_AUDIT_MAIL_FROM_NAME:-Octa M1 Audit}"
CEO_USER="${OCTA_M1_USER:-ceo}"
CEO_HOME="${OCTA_M1_CEO_HOME:-/Users/${CEO_USER}}"
REPO_ROOT="${OCTA_M1_REPO:-${CEO_HOME}/Developer/Repositories/octadecimal-agents/octadecimal.pro}"
SUDO_LOG="${OCTA_M1_SUDO_LOG:-/var/log/octa-sudo.log}"
LOG_DIR="${OCTA_M1_AUDIT_LOG_DIR:-/var/log/octa}"
REPORT_DIR="${OCTA_M1_AUDIT_REPORT_DIR:-${LOG_DIR}/m1-audit-reports}"
LOG_FILE="${OCTA_M1_AUDIT_LOG:-${LOG_DIR}/m1-security-audit.log}"
SKIP_MAIL="${OCTA_M1_AUDIT_SKIP_MAIL:-0}"

mkdir -p "${LOG_DIR}" "${REPORT_DIR}"

log() {
  printf '[%s] %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$*" >>"${LOG_FILE}"
}

section() {
  printf '\n== %s ==\n' "$*"
}

warn_lines=()

add_warn() {
  warn_lines+=("$*")
}

run_audit() {
  local ts host report warnings=0
  ts="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  host="$(scutil --get ComputerName 2>/dev/null || hostname -s)"

  report="$(mktemp "${REPORT_DIR}/m1-audit.XXXXXX")"
  {
    section "Octa M1 security audit"
    echo "timestamp_utc: ${ts}"
    echo "trigger: ${TRIGGER}"
    echo "host: ${host}"
    echo "hostname: $(hostname -f 2>/dev/null || hostname)"
    scutil <<< "show State:/Users/ConsoleUser" 2>/dev/null | grep -E "Name|UID" || true

    section "Uptime / load"
    uptime

    section "Power management"
    pmset -g 2>/dev/null || add_warn "pmset unavailable"
    if ! pmset -g 2>/dev/null | grep -q "SleepDisabled.*1"; then
      add_warn "SleepDisabled is not 1 — headless sleep risk"
    fi

    section "Workspace API (127.0.0.1:8042)"
    if health="$(curl -sf --connect-timeout 5 http://127.0.0.1:8042/workspace/health 2>/dev/null)"; then
      echo "${health}" | python3 -m json.tool 2>/dev/null || echo "${health}"
      if ! echo "${health}" | grep -q '"status"[[:space:]]*:[[:space:]]*"ok"'; then
        add_warn "Workspace health status is not ok"
      fi
    else
      add_warn "Workspace health unreachable on 127.0.0.1:8042"
      echo "unreachable"
    fi

    section "LaunchDaemon pl.octadecimal.workspace-api-m1-server"
    launchctl print system/pl.octadecimal.workspace-api-m1-server 2>&1 | grep -E "state|path|last exit|runs|pid" | head -12 \
      || add_warn "Workspace LaunchDaemon not loaded"

    section "Listening TCP (non-localhost)"
    local listeners
    listeners="$(lsof -nP -iTCP -sTCP:LISTEN 2>/dev/null | grep -v '127.0.0.1' | grep -v '^\COMMAND' || true)"
    if [[ -n "${listeners}" ]]; then
      echo "${listeners}"
      while IFS= read -r line; do
        [[ -z "${line}" ]] && continue
        if ! echo "${line}" | grep -qE ':22 \(LISTEN\)|sshd'; then
          add_warn "Unexpected LAN listener: ${line}"
        fi
      done <<< "${listeners}"
    else
      echo "(none besides possible ssh — verify manually)"
    fi

    section "Workspace bind check (LAN must fail)"
    lan_ip="$(ipconfig getifaddr en0 2>/dev/null || true)"
    if [[ -n "${lan_ip}" ]]; then
      if curl -sf --connect-timeout 2 "http://${lan_ip}:8042/workspace/health" >/dev/null 2>&1; then
        add_warn "Workspace exposed on LAN ${lan_ip}:8042"
        echo "FAIL: LAN reachable"
      else
        echo "OK: ${lan_ip}:8042 not reachable"
      fi
    else
      echo "skip: no en0 IPv4"
    fi

    section "Application firewall"
    /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate 2>/dev/null || true
    if /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate 2>/dev/null | grep -qi "disabled"; then
      add_warn "Application firewall disabled"
    fi

    section "Remote Login (SSH)"
    systemsetup -getremotelogin 2>/dev/null || true

    section "Disk space"
    df -h / /System/Volumes/Data 2>/dev/null | tail -n +2 || df -h /

    section "Knowledge sync marker"
    if [[ -f "${CEO_HOME}/Developer/Knowledge/.octa-sync/last-rsync-from-m5.txt" ]]; then
      echo "last_rsync_from_m5: $(cat "${CEO_HOME}/Developer/Knowledge/.octa-sync/last-rsync-from-m5.txt")"
    else
      add_warn "Knowledge sync marker missing on M1"
      echo "missing"
    fi

    section "Recent sudo (${SUDO_LOG})"
    if [[ -f "${SUDO_LOG}" ]]; then
      tail -30 "${SUDO_LOG}" 2>/dev/null || true
    else
      echo "sudo log not configured: ${SUDO_LOG}"
    fi

    section "Warnings"
    if [[ ${#warn_lines[@]} -gt 0 ]]; then
      warnings=${#warn_lines[@]}
      printf '%s\n' "${warn_lines[@]}"
    else
      echo "(none)"
    fi
    echo "warning_count: ${warnings}"

  } >"${report}"

  local archived="${REPORT_DIR}/$(date -u '+%Y%m%dT%H%M%SZ')-${TRIGGER}.txt"
  cp "${report}" "${archived}"
  log "report ${archived} trigger=${TRIGGER} warnings=${#warn_lines[@]}"

  if [[ "${SKIP_MAIL}" == "1" ]]; then
    cat "${report}"
    rm -f "${report}"
    return 0
  fi

  send_report_mail "${report}" "${#warn_lines[@]}"
  rm -f "${report}"
}

send_report_mail() {
  local report_file="$1"
  local warning_count="$2"
  local subject host
  host="$(scutil --get ComputerName 2>/dev/null || hostname -s)"
  subject="[M1 Audit/${TRIGGER}] ${host} — $(date -u '+%Y-%m-%d %H:%M UTC') — ${warning_count} warning(s)"

  {
    printf 'To: %s\n' "${MAIL_TO}"
    printf 'From: %s <%s>\n' "${MAIL_FROM_NAME}" "${MAIL_FROM}"
    printf 'Subject: %s\n' "${subject}"
    printf 'Content-Type: text/plain; charset=utf-8\n'
    printf 'Content-Transfer-Encoding: 8bit\n'
    printf '\n'
    cat "${report_file}"
  } | /usr/sbin/sendmail -t -f "${MAIL_FROM}"

  log "mail sent to ${MAIL_TO} subject=${subject}"
}

case "${1:-}" in
  --test-email)
    OCTA_M1_AUDIT_SKIP_MAIL=0
    TRIGGER=test
    report="$(mktemp)"
    {
      section "Test"
      echo "M1 audit mail pipeline OK at $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
    } >"${report}"
    send_report_mail "${report}" 0
    rm -f "${report}"
    echo "Test email queued to ${MAIL_TO}"
    ;;
  --report-only)
    OCTA_M1_AUDIT_SKIP_MAIL=1
    run_audit
    ;;
  "")
    run_audit
    ;;
  *)
    echo "Usage: $0 [--test-email | --report-only]" >&2
    exit 1
    ;;
esac
