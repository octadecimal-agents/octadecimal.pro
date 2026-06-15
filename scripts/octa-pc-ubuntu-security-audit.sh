#!/usr/bin/env bash
# PC Ubuntu security audit — email report to security@octadecimal.pl.
# Triggers: daily (cron), sudo (watch script), manual.
# Replaces legacy /usr/local/bin/system-monitor.sh (temp/load-only alerts).
set -euo pipefail

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

TRIGGER="${OCTA_PC_AUDIT_TRIGGER:-manual}"
MAIL_TO="${OCTA_PC_AUDIT_MAIL_TO:-security@octadecimal.pl}"
MAIL_FROM="${OCTA_PC_AUDIT_MAIL_FROM:-octadecimal@octadecimal.pl}"
MAIL_FROM_NAME="${OCTA_PC_AUDIT_MAIL_FROM_NAME:-Octa PC Ubuntu Audit}"
SUDO_LOG="${OCTA_PC_SUDO_LOG:-/var/log/octa-sudo.log}"
LOG_DIR="${OCTA_PC_AUDIT_LOG_DIR:-/var/log/octa}"
REPORT_DIR="${OCTA_PC_AUDIT_REPORT_DIR:-${LOG_DIR}/pc-ubuntu-audit-reports}"
LOG_FILE="${OCTA_PC_AUDIT_LOG:-${LOG_DIR}/pc-ubuntu-security-audit.log}"
SKIP_MAIL="${OCTA_PC_AUDIT_SKIP_MAIL:-0}"

if [[ "$(id -u)" -ne 0 ]]; then
  LOG_DIR="${HOME}/.octa"
  REPORT_DIR="${LOG_DIR}/pc-ubuntu-audit-reports"
  LOG_FILE="${LOG_DIR}/pc-ubuntu-security-audit.log"
fi

# Legacy thresholds (from system-monitor.sh)
TEMP_THRESHOLD="${OCTA_PC_TEMP_THRESHOLD:-85}"
RAM_THRESHOLD="${OCTA_PC_RAM_THRESHOLD:-90}"
SWAP_THRESHOLD="${OCTA_PC_SWAP_THRESHOLD:-50}"
ZOMBIE_THRESHOLD="${OCTA_PC_ZOMBIE_THRESHOLD:-10}"
SSH_FAIL_THRESHOLD="${OCTA_PC_SSH_FAIL_THRESHOLD:-10}"
LOAD_MULTIPLIER="${OCTA_PC_LOAD_MULTIPLIER:-1.5}"
DISK_WARN_PCT="${OCTA_PC_DISK_WARN_PCT:-85}"

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
  host="$(hostname -s)"

  report="$(mktemp "${REPORT_DIR}/pc-ubuntu-audit.XXXXXX")"
  {
    section "Octa PC Ubuntu security audit"
    echo "timestamp_utc: ${ts}"
    echo "trigger: ${TRIGGER}"
    echo "host: ${host}"
    echo "fqdn: $(hostname -f 2>/dev/null || hostname)"
    echo "tailscale: $(tailscale status --json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('Self',{}).get('DNSName','n/a'))" 2>/dev/null || echo 'n/a')"

    section "Uptime / load"
    uptime
    local cpu_cores load_1min load_threshold
    cpu_cores="$(nproc)"
    load_1min="$(uptime | awk -F'load average:' '{print $2}' | awk -F, '{print $1}' | tr -d ' ')"
    load_threshold="$(echo "${cpu_cores} * ${LOAD_MULTIPLIER}" | bc -l)"
    echo "cpu_cores: ${cpu_cores}  load_1m: ${load_1min}  threshold: ${load_threshold}"
    if (( $(echo "${load_1min} > ${load_threshold}" | bc -l) )); then
      add_warn "High load: ${load_1min} > ${load_threshold} (${cpu_cores} cores)"
    fi

    section "CPU temperature"
    if command -v sensors >/dev/null 2>&1; then
      sensors 2>/dev/null | grep -iE 'Tctl|Package id|Core 0' | head -5 || true
      local tctl
      tctl="$(sensors 2>/dev/null | grep -i 'Tctl' | awk '{print $2}' | tr -d '+°C' | cut -d'.' -f1)"
      if [[ -n "${tctl}" && "${tctl}" -gt "${TEMP_THRESHOLD}" ]]; then
        add_warn "CPU temperature critical: Tctl ${tctl}°C (threshold ${TEMP_THRESHOLD}°C)"
      fi
    else
      echo "sensors not installed"
    fi

    section "Memory / swap"
    free -h
    local mem_total mem_used mem_pct swap_total swap_used swap_pct
    read -r mem_total mem_used _ <<<"$(free -m | awk '/^Mem:/{print $2, $3, $4}')"
    mem_pct=$(( mem_used * 100 / mem_total ))
    echo "ram_used_pct: ${mem_pct}%"
    if [[ "${mem_pct}" -gt "${RAM_THRESHOLD}" ]]; then
      add_warn "High RAM: ${mem_pct}% (threshold ${RAM_THRESHOLD}%)"
    fi
    read -r swap_total swap_used _ <<<"$(free -m | awk '/^Swap:/{print $2, $3, $4}')"
    if [[ "${swap_total}" -gt 0 ]]; then
      swap_pct=$(( swap_used * 100 / swap_total ))
      echo "swap_used_pct: ${swap_pct}%"
      if [[ "${swap_pct}" -gt "${SWAP_THRESHOLD}" ]]; then
        add_warn "High swap: ${swap_pct}% (threshold ${SWAP_THRESHOLD}%)"
      fi
    fi

    section "Disk space"
    df -h / /home 2>/dev/null | tail -n +2 || df -h /
    while read -r pct mount; do
      pct_num="${pct%%%}"
      if [[ "${pct_num}" =~ ^[0-9]+$ && "${pct_num}" -ge "${DISK_WARN_PCT}" ]]; then
        add_warn "Disk usage ${pct} on ${mount}"
      fi
    done < <(df -P / /home 2>/dev/null | awk 'NR>1 {print $5, $6}')

    section "Docker containers"
    if command -v docker >/dev/null 2>&1; then
      local total running unhealthy
      total="$(docker ps -aq 2>/dev/null | wc -l | tr -d ' ')"
      running="$(docker ps -q 2>/dev/null | wc -l | tr -d ' ')"
      unhealthy="$(docker ps --filter health=unhealthy -q 2>/dev/null | wc -l | tr -d ' ')"
      echo "total: ${total}  running: ${running}  unhealthy: ${unhealthy}"
      docker ps --format 'table {{.Names}}\t{{.Status}}' 2>/dev/null | head -25
      if [[ "${unhealthy}" -gt 0 ]]; then
        add_warn "Docker unhealthy containers: ${unhealthy}"
      fi
      local exited
      exited="$(docker ps -a --filter status=exited -q 2>/dev/null | wc -l | tr -d ' ')"
      if [[ "${exited}" -gt 5 ]]; then
        add_warn "Many exited containers: ${exited}"
      fi
    else
      echo "docker not available"
    fi

    section "Key local services (HTTP)"
    for url in \
      "http://127.0.0.1:6333/collections" \
      "http://127.0.0.1:5678/healthz" \
      "http://127.0.0.1:3000/api/health" \
      "http://127.0.0.1:8042/workspace/health"; do
      if curl -sf --connect-timeout 3 "${url}" >/dev/null 2>&1; then
        echo "OK  ${url}"
      else
        echo "FAIL ${url}"
      fi
    done

    section "Listening TCP (non-localhost)"
    ss -tlnp 2>/dev/null | grep -v '127.0.0.1' | grep -v '::1' | head -30 || true

    section "Firewall (UFW)"
    if command -v ufw >/dev/null 2>&1; then
      ufw status verbose 2>/dev/null | head -15 || add_warn "UFW status unavailable"
      if ufw status 2>/dev/null | grep -q inactive; then
        add_warn "UFW inactive"
      fi
    else
      echo "ufw not installed"
    fi

    section "SSH failed logins (last hour)"
    local auth_log fail_count
    auth_log=""
    for p in /var/log/auth.log /var/log/secure; do
      [[ -f "${p}" ]] && auth_log="${p}" && break
    done
    if [[ -n "${auth_log}" && -r "${auth_log}" ]]; then
      fail_count="$(grep "Failed password" "${auth_log}" 2>/dev/null | awk -v d="$(date '+%b %e %H')" '$0 ~ d' | wc -l | tr -d ' ')" || fail_count=0
      echo "failed_password_last_hour: ${fail_count} (log: ${auth_log})"
      if [[ "${fail_count}" -gt "${SSH_FAIL_THRESHOLD}" ]]; then
        add_warn "SSH brute-force signals: ${fail_count} failures/hour"
        grep "Failed password" "${auth_log}" 2>/dev/null | awk -v d="$(date '+%b %e %H')" '$0 ~ d' \
          | grep -oP 'from \K[\d.]+' 2>/dev/null | sort | uniq -c | sort -rn | head -5 || true
      fi
    elif [[ -n "${auth_log}" ]]; then
      echo "auth.log not readable (run as root or adm group)"
    fi

    section "Zombie processes"
    local zombie_count
    zombie_count="$(ps axo stat= 2>/dev/null | grep -c '^Z' 2>/dev/null || true)"
    zombie_count="${zombie_count:-0}"
    echo "zombie_count: ${zombie_count}"
    if [[ "${zombie_count}" -gt "${ZOMBIE_THRESHOLD}" ]]; then
      add_warn "Zombie processes: ${zombie_count}"
      ps axo pid,stat,cmd | awk '$2 ~ /Z/' | head -10 || true
    fi

    section "Pending security updates"
    if command -v apt-get >/dev/null 2>&1; then
      { apt-get -s upgrade 2>/dev/null | grep -i security | head -10; } || echo "(none or apt locked)"
    fi

    section "Recent sudo (${SUDO_LOG})"
    if [[ -f "${SUDO_LOG}" ]]; then
      tail -30 "${SUDO_LOG}" 2>/dev/null || true
    else
      echo "sudo log not configured: ${SUDO_LOG}"
    fi

    section "Boot time"
    who -b 2>/dev/null || true
    local boot_flag boot_current boot_last
    boot_flag="${OCTA_PC_AUDIT_STATE_DIR:-/var/lib/octa}/pc-ubuntu-last-boot"
    if [[ "$(id -u)" -ne 0 ]]; then
      boot_flag="${HOME}/.octa/pc-ubuntu-last-boot"
    fi
    boot_current="$(who -b 2>/dev/null | awk '{print $3, $4}' || true)"
    if [[ -n "${boot_current}" ]]; then
      if [[ -f "${boot_flag}" ]]; then
        boot_last="$(cat "${boot_flag}")"
        if [[ "${boot_current}" != "${boot_last}" ]]; then
          add_warn "Server rebooted: was ${boot_last}, now ${boot_current}"
        fi
      fi
      mkdir -p "$(dirname "${boot_flag}")"
      printf '%s\n' "${boot_current}" >"${boot_flag}"
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

  if [[ "${OCTA_PC_AUDIT_MAIL_ONLY_IF_WARN:-0}" == "1" && ${#warn_lines[@]} -eq 0 ]]; then
    log "skip mail — no warnings (legacy alert-only mode)"
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
  host="$(hostname -s)"
  subject="[PC Ubuntu Audit/${TRIGGER}] ${host} — $(date -u '+%Y-%m-%d %H:%M UTC') — ${warning_count} warning(s)"

  {
    printf 'To: %s\n' "${MAIL_TO}"
    printf 'From: %s <%s>\n' "${MAIL_FROM_NAME}" "${MAIL_FROM}"
    printf 'Subject: %s\n' "${subject}"
    printf 'Content-Type: text/plain; charset=utf-8\n'
    printf 'Content-Transfer-Encoding: 8bit\n'
    printf '\n'
    cat "${report_file}"
  } | sendmail -t -f "${MAIL_FROM}" 2>/dev/null || sendmail "${MAIL_TO}" <"${report_file}"

  log "mail sent to ${MAIL_TO} subject=${subject}"
}

case "${1:-}" in
  --test-email)
    TRIGGER=test
    report="$(mktemp)"
    { section "Test"; echo "PC Ubuntu audit mail OK at $(date -u '+%Y-%m-%dT%H:%M:%SZ')"; } >"${report}"
    send_report_mail "${report}" 0
    rm -f "${report}"
    echo "Test email queued to ${MAIL_TO}"
    ;;
  --report-only)
    SKIP_MAIL=1
    run_audit
    ;;
  --legacy-alert-only)
    OCTA_PC_AUDIT_MAIL_ONLY_IF_WARN=1
    SKIP_MAIL="${OCTA_PC_AUDIT_SKIP_MAIL:-0}"
    TRIGGER=alert
    run_audit
    ;;
  "")
    run_audit
    ;;
  *)
    echo "Usage: $0 [--test-email | --report-only | --legacy-alert-only]" >&2
    exit 1
    ;;
esac
