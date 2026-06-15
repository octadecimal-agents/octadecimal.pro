#!/usr/bin/env bash
# One-shot: LaunchDaemon + pmset for M1 headless (closed lid, AC power).
# Run on M1 as admin: sudo ./scripts/m1-headless-server-setup.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INSTALL="${REPO_ROOT}/scripts/install-workspace-api-m1-launchd.sh"
CEO_USER="${OCTA_M1_USER:-ceo}"
CEO_REPO="${OCTA_M1_REPO:-/Users/${CEO_USER}/Developer/Repositories/octadecimal-agents/octadecimal.pro}"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run as root on M1:" >&2
  echo "  sudo OCTA_M1_REPO=${CEO_REPO} $0" >&2
  exit 1
fi

if [[ ! -x "${INSTALL}" ]]; then
  echo "Missing installer: ${INSTALL}" >&2
  exit 1
fi

echo "==> Stopping LaunchAgent (if any)..."
"${INSTALL}" --uninstall-agent || true

echo "==> Installing LaunchDaemon as ${CEO_USER}..."
OCTA_M1_REPO="${CEO_REPO}" OCTA_M1_USER="${CEO_USER}" \
  OCTA_WORKSPACE_SKIP_UV_SYNC="${OCTA_WORKSPACE_SKIP_UV_SYNC:-1}" \
  "${INSTALL}" --daemon

echo "==> Configuring pmset (headless / closed lid on AC)..."
pmset -a disablesleep 1
pmset -a autorestart 1
pmset -a sleep 0 displaysleep 0 disksleep 0 standby 0 autopoweroff 0
pmset -a womp 1 tcpkeepalive 1

echo ""
echo "==> pmset (AC):"
pmset -g custom | sed -n '/AC Power:/,/Battery Power:/p' | head -20

echo ""
echo "==> launchd:"
launchctl print "system/pl.octadecimal.workspace-api-m1-server" 2>&1 | grep -E "state|path" | head -4

echo ""
echo "==> health (as ${CEO_USER}):"
sudo -u "${CEO_USER}" curl -sf http://127.0.0.1:8042/workspace/health | python3 -m json.tool

echo ""
echo "Done. Optional: plug dummy HDMI, close lid, verify from M5:"
echo "  ssh m1-ceo 'curl -sf http://127.0.0.1:8042/workspace/health'"
