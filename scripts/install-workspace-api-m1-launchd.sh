#!/usr/bin/env bash
# Install Octa Workspace on M1 (server mode, localhost:8042).
#   LaunchAgent (gui) — when CEO has a console GUI session
#   LaunchDaemon (system) — when console user is admin but Workspace runs as ceo
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
AGENT_TEMPLATE="${REPO_ROOT}/scripts/launchd/pl.octadecimal.workspace-api-m1.plist.template"
DAEMON_TEMPLATE="${REPO_ROOT}/scripts/launchd/pl.octadecimal.workspace-api-m1-server.plist.template"
AGENT_LABEL="pl.octadecimal.workspace-api-m1"
DAEMON_LABEL="pl.octadecimal.workspace-api-m1-server"
DEV_LABEL="pl.octadecimal.workspace-api-dev"
CEO_USER="${OCTA_M1_USER:-ceo}"
CEO_HOME="$(eval echo "~${CEO_USER}")"
CEO_REPO="${OCTA_M1_REPO:-${CEO_HOME}/Developer/Repositories/octadecimal-agents/octadecimal.pro}"
GUI_UID="$(id -u)"

# When Admin runs sudo, HOME can stay /Users/admin — force ceo context for uv/launchd.
run_as_ceo() {
  sudo -u "${CEO_USER}" env \
    HOME="${CEO_HOME}" \
    USER="${CEO_USER}" \
    LOGNAME="${CEO_USER}" \
    PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin" \
    "$@"
}

uv_sync_for_ceo() {
  if [[ "${OCTA_WORKSPACE_SKIP_UV_SYNC:-0}" == "1" ]]; then
    echo "Skipping uv sync (OCTA_WORKSPACE_SKIP_UV_SYNC=1)"
    return 0
  fi
  if [[ -d "${CEO_REPO}/.venv" ]] && [[ "$(stat -f '%Su' "${CEO_REPO}/.venv" 2>/dev/null || echo '')" == "${CEO_USER}" ]]; then
    echo "Using existing .venv owned by ${CEO_USER} (set OCTA_WORKSPACE_SKIP_UV_SYNC=1 to skip sync)"
  fi
  echo "Syncing dependencies as ${CEO_USER}..."
  run_as_ceo bash -c "cd '${CEO_REPO}' && uv sync"
}

stop_port_8042() {
  local pids
  pids="$(lsof -ti :8042 2>/dev/null || true)"
  if [[ -n "${pids}" ]]; then
    echo "Stopping process on :8042 (${pids})..."
    kill ${pids} 2>/dev/null || true
    sleep 2
  fi
}

uninstall_agent() {
  local uid="${GUI_UID}"
  if [[ "$(id -u)" -eq 0 ]]; then
    uid="$(id -u "${CEO_USER}")"
  fi
  launchctl bootout "gui/${uid}/${AGENT_LABEL}" 2>/dev/null || true
  rm -f "${CEO_HOME}/Library/LaunchAgents/pl.octadecimal.workspace-api-m1.plist"
  echo "Removed LaunchAgent ${AGENT_LABEL}"
}

uninstall_daemon() {
  if [[ "$(id -u)" -ne 0 ]]; then
    echo "Use: sudo $0 --uninstall-daemon" >&2
    exit 1
  fi
  launchctl bootout "system/${DAEMON_LABEL}" 2>/dev/null || true
  rm -f "/Library/LaunchDaemons/pl.octadecimal.workspace-api-m1-server.plist"
  echo "Removed LaunchDaemon ${DAEMON_LABEL}"
}

install_daemon() {
  if [[ "$(id -u)" -ne 0 ]]; then
    echo "LaunchDaemon install requires root. Run on M1:" >&2
    echo "  sudo OCTA_M1_REPO=${CEO_REPO} $0 --daemon" >&2
    exit 1
  fi
  if [[ ! -d "${CEO_REPO}" ]]; then
    echo "CEO repo not found: ${CEO_REPO}" >&2
    exit 1
  fi
  if [[ ! -f "${DAEMON_TEMPLATE}" ]]; then
    echo "Missing template: ${DAEMON_TEMPLATE}" >&2
    exit 1
  fi

  echo "Installing system LaunchDaemon as user ${CEO_USER}..."
  mkdir -p "${CEO_HOME}/.octa/logs"
  uv_sync_for_ceo
  run_as_ceo env OCTA_WORKSPACE_SKIP_UV_SYNC=1 "${CEO_REPO}/scripts/octa-workspace-api-m1.sh" --seed-only

  stop_port_8042

  local dest="/Library/LaunchDaemons/pl.octadecimal.workspace-api-m1-server.plist"
  sed -e "s|@REPO_ROOT@|${CEO_REPO}|g" \
      -e "s|@CEO_HOME@|${CEO_HOME}|g" \
      -e "s|@CEO_USER@|${CEO_USER}|g" \
      "${DAEMON_TEMPLATE}" >"${dest}"
  chmod 644 "${dest}"
  chown root:wheel "${dest}"

  launchctl bootout "system/${DAEMON_LABEL}" 2>/dev/null || true
  launchctl bootstrap system "${dest}"
  launchctl enable "system/${DAEMON_LABEL}"
  launchctl kickstart -k "system/${DAEMON_LABEL}"

  echo ""
  echo "Installed LaunchDaemon: ${dest}"
  echo "  Label:  ${DAEMON_LABEL}"
  echo "  User:   ${CEO_USER}"
  echo "  URL:    http://127.0.0.1:8042/"
  echo "  Log:    ${CEO_HOME}/.octa/logs/workspace-api-m1.log"
}

install_agent() {
  local dest="${CEO_HOME}/Library/LaunchAgents/pl.octadecimal.workspace-api-m1.plist"
  if [[ "$(whoami)" != "${CEO_USER}" && "$(id -u)" -ne 0 ]]; then
    echo "LaunchAgent install must run as ${CEO_USER} (now: $(whoami))" >&2
    exit 1
  fi
  if [[ ! -f "${AGENT_TEMPLATE}" ]]; then
    echo "Missing template: ${AGENT_TEMPLATE}" >&2
    exit 1
  fi

  mkdir -p "${CEO_HOME}/Library/LaunchAgents" "${CEO_HOME}/.octa/logs"
  echo "Syncing dependencies..."
  (cd "${REPO_ROOT}" && uv sync)
  echo "Seeding demo data..."
  OCTA_WORKSPACE_SKIP_UV_SYNC=1 "${REPO_ROOT}/scripts/octa-workspace-api-m1.sh" --seed-only
  stop_port_8042

  sed -e "s|@REPO_ROOT@|${REPO_ROOT}|g" -e "s|@HOME@|${CEO_HOME}|g" "${AGENT_TEMPLATE}" >"${dest}"

  if ! launchctl print "gui/${GUI_UID}" >/dev/null 2>&1; then
    echo ""
    echo "Plist written: ${dest}"
    echo "ERROR: gui/${GUI_UID} unavailable — $(whoami) has no Aqua session."
    echo "  Console user is probably 'admin', not '${CEO_USER}'."
    echo "  Use LaunchDaemon instead (works without CEO GUI login):"
    echo "    sudo OCTA_M1_REPO=${REPO_ROOT} $0 --daemon"
    exit 1
  fi

  launchctl bootout "gui/${GUI_UID}/${AGENT_LABEL}" 2>/dev/null || true
  launchctl bootstrap "gui/${GUI_UID}" "${dest}"
  launchctl enable "gui/${GUI_UID}/${AGENT_LABEL}"
  launchctl kickstart -k "gui/${GUI_UID}/${AGENT_LABEL}"

  echo ""
  echo "Installed LaunchAgent: ${dest}"
  echo "  Label: ${AGENT_LABEL}"
}

case "${1:-}" in
  --uninstall)
    uninstall_agent
    if [[ "$(id -u)" -eq 0 ]]; then
      uninstall_daemon
    else
      echo "For daemon removal: sudo $0 --uninstall-daemon"
    fi
    ;;
  --uninstall-agent) uninstall_agent ;;
  --uninstall-daemon) uninstall_daemon ;;
  --daemon) install_daemon ;;
  "")
    if launchctl print "gui/${GUI_UID}" >/dev/null 2>&1; then
      install_agent
    else
      echo "No gui/${GUI_UID} domain — recommending LaunchDaemon."
      echo "Run: sudo OCTA_M1_REPO=${CEO_REPO} $0 --daemon"
      exit 1
    fi
    ;;
  *)
    echo "Usage: $0 [--daemon | --uninstall | --uninstall-agent | --uninstall-daemon]" >&2
    exit 1
    ;;
esac

echo ""
echo "Verify: curl -s http://127.0.0.1:8042/workspace/health | python3 -m json.tool"
echo "Calendar (M1 headless): sudo ${REPO_ROOT}/scripts/install-m1-calendar-automation.sh"
echo "Runbook: docs/runbooks/workspace-m1-server-mode.md"
