#!/usr/bin/env bash
# One-shot M1 calendar automation: PPPC profile (TCC) + LaunchAgent cache sync.
# Run on M1 as admin: sudo ./scripts/install-m1-calendar-automation.sh
# From M5: ./scripts/install-m1-calendar-automation.sh --remote m1-admin
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CEO_USER="${OCTA_M1_USER:-ceo}"
CEO_HOME="$(eval echo "~${CEO_USER}")"
CEO_REPO="${OCTA_M1_REPO:-${CEO_HOME}/Developer/Repositories/octadecimal-agents/octadecimal.pro}"
PROFILE_ID="pl.octadecimal.m1-calendar-pppc"
REMOTE_HOST=""

usage() {
  cat <<EOF
Usage: $(basename "$0") [--remote SSH_HOST]

Installs on M1:
  1. Privacy profile (Calendars) for Python used by uv
  2. LaunchAgent — hourly EventKit → ~/.octa/calendar-cache.json
  3. Kickstarts first sync

Workspace LaunchDaemon should use CALENDAR_PROVIDER=cache (see plist template).

Requires: root on M1 (sudo). From M5 use --remote m1-admin.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --remote)
      REMOTE_HOST="${2:?host}"
      shift 2
      ;;
    -h | --help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -n "${REMOTE_HOST}" ]]; then
  echo "Running on ${REMOTE_HOST} via SSH..."
  rsync -az "${REPO_ROOT}/scripts/" "${REMOTE_HOST}:${CEO_REPO}/scripts/"
  ssh "${REMOTE_HOST}" "sudo OCTA_M1_REPO=${CEO_REPO} OCTA_M1_USER=${CEO_USER} bash ${CEO_REPO}/scripts/install-m1-calendar-automation.sh"
  exit 0
fi

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run with sudo on M1." >&2
  exit 1
fi

if [[ ! -d "${CEO_REPO}/.venv" ]]; then
  echo "Missing venv: ${CEO_REPO}/.venv — run uv sync as ${CEO_USER} first." >&2
  exit 1
fi

PYTHON="$("${CEO_REPO}/.venv/bin/python" -c 'import sys; print(sys.executable)' 2>/dev/null || true)"
if [[ -z "${PYTHON}" || ! -x "${PYTHON}" ]]; then
  PYTHON="${CEO_REPO}/.venv/bin/python"
fi

CODE_REQ="$(codesign -dr - "${PYTHON}" 2>&1 | sed -n 's/.*=> //p' | head -1 || true)"

PROFILE_DIR="${CEO_REPO}/data/m1-pppc"
mkdir -p "${PROFILE_DIR}"
PROFILE_PATH="${PROFILE_DIR}/octa-m1-calendar.mobileconfig"
PAYLOAD_UUID="$(uuidgen)"
ROOT_UUID="$(uuidgen)"

# shellcheck disable=SC2154
cat >"${PROFILE_PATH}" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>PayloadContent</key>
  <array>
    <dict>
      <key>PayloadDisplayName</key>
      <string>Octa Calendar TCC</string>
      <key>PayloadIdentifier</key>
      <string>${PROFILE_ID}.inner</string>
      <key>PayloadType</key>
      <string>com.apple.TCC.configuration-profile-policy</string>
      <key>PayloadUUID</key>
      <string>${PAYLOAD_UUID}</string>
      <key>PayloadVersion</key>
      <integer>1</integer>
      <key>Services</key>
      <dict>
        <key>Calendar</key>
        <array>
          <dict>
            <key>Identifier</key>
            <string>${PYTHON}</string>
            <key>IdentifierType</key>
            <string>path</string>
            <key>Allowed</key>
            <true/>
$(if [[ -n "${CODE_REQ}" ]]; then echo "            <key>CodeRequirement</key>
            <string>${CODE_REQ}</string>"; fi)
          </dict>
        </array>
      </dict>
    </dict>
  </array>
  <key>PayloadDisplayName</key>
  <string>Octa M1 Calendar (PPPC)</string>
  <key>PayloadIdentifier</key>
  <string>${PROFILE_ID}</string>
  <key>PayloadOrganization</key>
  <string>Octadecimal</string>
  <key>PayloadRemovalDisallowed</key>
  <false/>
  <key>PayloadType</key>
  <string>Configuration</string>
  <key>PayloadUUID</key>
  <string>${ROOT_UUID}</string>
  <key>PayloadVersion</key>
  <integer>1</integer>
</dict>
</plist>
EOF

echo "Generated PPPC profile: ${PROFILE_PATH}"
echo "  Python: ${PYTHON}"

if profiles list 2>/dev/null | grep -q "${PROFILE_ID}"; then
  echo "Removing previous profile ${PROFILE_ID}..."
  profiles remove -identifier="${PROFILE_ID}" 2>/dev/null || true
fi

if profiles install -path="${PROFILE_PATH}"; then
  echo "Installed PPPC profile ${PROFILE_ID}"
else
  echo "WARNING: profiles install failed — approve manually in System Settings → Profiles" >&2
  echo "  open ${PROFILE_PATH}" >&2
fi

OCTA_M1_REPO="${CEO_REPO}" OCTA_M1_USER="${CEO_USER}" bash "${CEO_REPO}/scripts/install-calendar-sync-m1-launchd.sh"

WS_PLIST="/Library/LaunchDaemons/pl.octadecimal.workspace-api-m1-server.plist"
if [[ -f "${WS_PLIST}" ]]; then
  /usr/libexec/PlistBuddy -c "Set :EnvironmentVariables:CALENDAR_PROVIDER cache" "${WS_PLIST}" 2>/dev/null \
    && echo "Updated ${WS_PLIST} → CALENDAR_PROVIDER=cache" \
    || echo "Note: reinstall Workspace daemon plist for CALENDAR_PROVIDER=cache"
fi

echo ""
echo "First calendar sync (as ${CEO_USER})..."
if sudo -u "${CEO_USER}" env HOME="${CEO_HOME}" PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin" \
  bash "${CEO_REPO}/scripts/octa-calendar-sync-m1.sh"; then
  echo "Calendar cache OK."
else
  echo "First sync failed — if gui/${CEO_USER} has no session, log in at console once or wait for LaunchAgent." >&2
fi

echo ""
echo "Restart Workspace LaunchDaemon to pick up cache mode:"
echo "  launchctl kickstart -k system/pl.octadecimal.workspace-api-m1-server"
echo ""
echo "Verify from M5:"
echo "  ./scripts/octa workspace smoke --remote m1-ceo --strict-calendar"
