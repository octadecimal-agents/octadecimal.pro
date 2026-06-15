#!/usr/bin/env bash
# M5.6 — smoke checks for M1 server mode (local or via SSH from M5).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOST="${WORKSPACE_HOST:-127.0.0.1}"
PORT="${WORKSPACE_PORT:-8042}"
BASE_URL="http://${HOST}:${PORT}"
HEALTH_URL="${BASE_URL}/workspace/health"
CHAT_URL="${BASE_URL}/workspace/chat"
PLAN_URL="${BASE_URL}/workspace/planning/calendar"
SSH_HOST="${OCTA_M1_SSH_HOST:-}"
JSON_OUT=0
STRICT_CALENDAR=0
FAILURES=0
WARNINGS=0

usage() {
  cat <<EOF
Usage: $(basename "$0") [options]

Options:
  --remote HOST   Run checks on M1 via ssh (e.g. m1-ceo)
  --json          Machine-readable summary
  --strict-calendar  Fail unless calendar_source is macos or fresh cache (M1 headless)
  -h              Help

Examples:
  $(basename "$0")                    # on M1
  $(basename "$0") --remote m1-ceo    # from M5
  octa workspace smoke --remote m1-ceo
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --remote)
      SSH_HOST="${2:?missing host after --remote}"
      shift 2
      ;;
    --json)
      JSON_OUT=1
      shift
      ;;
    --strict-calendar)
      STRICT_CALENDAR=1
      shift
      ;;
    -h | --help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

remote() {
  if [[ -n "${SSH_HOST}" ]]; then
    ssh -o BatchMode=yes "${SSH_HOST}" "$@"
  else
    "$@"
  fi
}

run_on_target() {
  local cmd="$1"
  if [[ -n "${SSH_HOST}" ]]; then
    ssh -o BatchMode=yes "${SSH_HOST}" "bash -lc $(printf '%q' "${cmd}")"
  else
    bash -lc "${cmd}"
  fi
}

pass() {
  if [[ "${JSON_OUT}" -eq 0 ]]; then
    echo "  OK   $*"
  fi
}

fail() {
  FAILURES=$((FAILURES + 1))
  if [[ "${JSON_OUT}" -eq 0 ]]; then
    echo "  FAIL $*" >&2
  fi
}

warn() {
  WARNINGS=$((WARNINGS + 1))
  if [[ "${JSON_OUT}" -eq 0 ]]; then
    echo "  WARN $*"
  fi
}

check_health() {
  local body
  if ! body="$(run_on_target "curl -sf '${HEALTH_URL}'")"; then
    fail "GET /workspace/health — connection refused or non-200"
    return 1
  fi
  pass "GET /workspace/health"

  local status calendar_source review_pending
  status="$(python3 -c "import json,sys; print(json.load(sys.stdin).get('status',''))" <<<"${body}")"
  calendar_source="$(python3 -c "import json,sys; print(json.load(sys.stdin).get('calendar_source',''))" <<<"${body}")"
  review_pending="$(python3 -c "import json,sys; print(json.load(sys.stdin).get('review_pending_count',0))" <<<"${body}")"

  if [[ "${status}" == "ok" || "${status}" == "degraded" ]]; then
    pass "health.status=${status}"
  else
    fail "health.status=${status} (expected ok|degraded)"
  fi

  if [[ "${review_pending}" =~ ^[0-9]+$ ]] && [[ "${review_pending}" -ge 0 ]]; then
    pass "review_pending_count=${review_pending}"
  else
    fail "review_pending_count invalid"
  fi

  case "${calendar_source}" in
    macos | calctl)
      pass "calendar_source=${calendar_source} (live)"
      ;;
    cache)
      if cache_is_fresh; then
        pass "calendar_source=cache (headless M1 — fresh sync)"
      elif [[ "${STRICT_CALENDAR}" -eq 1 ]]; then
        fail "calendar_source=cache stale — run install-m1-calendar-automation.sh on M1"
      else
        warn "calendar_source=cache — run calendar sync or PPPC install"
      fi
      ;;
    fixture*)
      if [[ "${STRICT_CALENDAR}" -eq 1 ]]; then
        fail "calendar_source=${calendar_source} — grant Calendars on M1 (see macos-calendar-permissions runbook)"
      else
        warn "calendar_source=${calendar_source} — grant Calendars on M1 for live #Planning"
      fi
      ;;
    *)
      warn "calendar_source=${calendar_source} (unexpected)"
      ;;
  esac

  HEALTH_BODY="${body}"
}

check_chat() {
  local body
  if ! body="$(run_on_target "curl -sf -X POST '${CHAT_URL}' -H 'Content-Type: application/json' -d '{\"message\":\"smoke test M5.6\",\"active_hash\":\"#Ogolny\"}'")"; then
    fail "POST /workspace/chat"
    return
  fi
  if python3 -c "import json,sys; m=json.load(sys.stdin).get('message',''); sys.exit(0 if m else 1)" <<<"${body}"; then
    pass "POST /workspace/chat — reply received"
  else
    fail "POST /workspace/chat — empty message"
  fi
}

check_plan() {
  if run_on_target "curl -sf '${PLAN_URL}' >/dev/null"; then
    pass "GET /workspace/planning/calendar"
  else
    fail "GET /workspace/planning/calendar"
  fi
}

check_launchd() {
  local out
  out="$(run_on_target '
    if launchctl print system/pl.octadecimal.workspace-api-m1-server 2>/dev/null | grep -q "state = running"; then
      echo daemon
    elif launchctl print "gui/$(id -u)/pl.octadecimal.workspace-api-m1" 2>/dev/null | grep -q "state = running"; then
      echo agent
    else
      echo missing
    fi
  ')" || out="missing"

  case "${out}" in
    daemon)
      pass "launchd LaunchDaemon running"
      ;;
    agent)
      pass "launchd LaunchAgent running"
      ;;
    *)
      warn "launchd job not running (manual octa-mvp-up.sh?)"
      ;;
  esac
}

check_binding() {
  if [[ "${HOST}" != "127.0.0.1" && "${HOST}" != "localhost" ]]; then
    warn "WORKSPACE_HOST=${HOST} (M5.6 expects 127.0.0.1 on M1)"
  else
    pass "binding ${HOST}:${PORT} (localhost)"
  fi
}

cache_is_fresh() {
  local cache_path="${OCTA_CALENDAR_CACHE:-${HOME}/.octa/calendar-cache.json}"
  local check_cmd="test -f '${cache_path}' && python3 -c \"import json,sys;from datetime import date; d=json.load(open('${cache_path}')); sys.exit(0 if d.get('date')==date.today().isoformat() else 1)\""
  if [[ -n "${SSH_HOST}" ]]; then
    ssh -o BatchMode=yes "${SSH_HOST}" "bash -lc $(printf '%q' "${check_cmd}")"
  else
    bash -lc "${check_cmd}"
  fi
}

if [[ "${JSON_OUT}" -eq 0 ]]; then
  echo "Octa M1 smoke check — ${BASE_URL}"
  [[ -n "${SSH_HOST}" ]] && echo "  via ssh ${SSH_HOST}"
  echo ""
fi

HEALTH_BODY=""
check_binding
check_health || true
if [[ -n "${HEALTH_BODY:-}" ]]; then
  check_chat
  check_plan
fi
check_launchd

if [[ "${JSON_OUT}" -eq 1 ]]; then
  export HEALTH_BODY
  python3 - <<PY
import json, os
raw = os.environ.get("HEALTH_BODY") or ""
body = json.loads(raw) if raw else {}
print(json.dumps({
  "base_url": "${BASE_URL}",
  "ssh_host": "${SSH_HOST}" or None,
  "failures": ${FAILURES},
  "warnings": ${WARNINGS},
  "health": body,
  "pass": ${FAILURES} == 0,
}, indent=2))
PY
  if [[ "${FAILURES}" -gt 0 ]]; then
    exit 1
  fi
  exit 0
else
  echo ""
  echo "Summary: ${FAILURES} failure(s), ${WARNINGS} warning(s)"
  if [[ "${FAILURES}" -gt 0 ]]; then
    echo "Result: FAIL"
    exit 1
  fi
  if [[ "${WARNINGS}" -gt 0 ]]; then
    echo "Result: PASS with warnings (calendar permission pending for full M5.6.3)"
    exit 0
  fi
  echo "Result: PASS"
fi

if [[ "${FAILURES}" -gt 0 ]]; then
  exit 1
fi
