#!/usr/bin/env bash
# Trigger macOS Calendars TCC prompt on M1 — must run in Terminal.app on M1 (GUI), NOT over SSH.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${REPO_ROOT}"

export CALENDAR_PROVIDER="${CALENDAR_PROVIDER:-auto}"
export KNOWLEDGE_ROOT="${KNOWLEDGE_ROOT:-${HOME}/Developer/Knowledge}"
export WORKSPACE_ENABLED=1

PYTHON="${REPO_ROOT}/.venv/bin/python"
if [[ -L "${PYTHON}" ]]; then
  PYTHON_RESOLVED="$(readlink "${PYTHON}")"
  if [[ "${PYTHON_RESOLVED}" != /* ]]; then
    PYTHON_RESOLVED="${REPO_ROOT}/.venv/bin/${PYTHON_RESOLVED}"
  fi
else
  PYTHON_RESOLVED="${PYTHON}"
fi

echo ""
echo "=== Octa — bootstrap uprawnień Kalendarz (M1) ==="
echo ""
echo "Workspace (launchd) czyta kalendarz przez Python/calctl, NIE przez Terminal."
echo "macOS musi zezwolić binarce Python na dostęp do Kalendarzy."
echo ""
echo "Binarce do włączenia w Ustawieniach → Prywatność → Kalendarze:"
echo "  ${PYTHON_RESOLVED}"
echo "  (symlink: ${PYTHON})"
echo ""
echo "Uruchamiam test odczytu — powinien pojawić się dialog macOS."
echo "Jeśli dialogu nie ma, otwórz ręcznie:"
echo "  Ustawienia systemowe → Prywatność i ochrona → Kalendarze"
echo "  Włącz: Python  (lub ścieżka powyżej)"
echo ""
read -r -p "Naciśnij Enter (M1, Terminal.app, konto ceo)..." _

set +e
OUTPUT="$(uv run python - <<'PY' 2>&1
import asyncio
from secure_agentic_ai.infrastructure.workspace.config import WorkspaceConfig
from secure_agentic_ai.infrastructure.macos.calendar_provider import list_today_calendar_events

async def main():
    config = WorkspaceConfig.from_env()
    events, source = await list_today_calendar_events(config)
    print(f"source={source} events={len(events)}")
    for e in events[:5]:
        print(f"  {e.time} {e.title}")

asyncio.run(main())
PY
)"
RC=$?
set -e

echo "${OUTPUT}"

if echo "${OUTPUT}" | grep -q 'source=macos'; then
  echo ""
  echo "OK — Kalendarz live. Restart Workspace launchd:"
  if launchctl print system/pl.octadecimal.workspace-api-m1-server >/dev/null 2>&1; then
    echo "  sudo launchctl kickstart -k system/pl.octadecimal.workspace-api-m1-server"
  else
    echo "  launchctl kickstart -k gui/\$(id -u)/pl.octadecimal.workspace-api-m1"
  fi
  exit 0
fi

echo ""
echo "Nadal brak dostępu (source=fixture-denied lub fixture)."
echo ""
echo "Co sprawdzić:"
echo "  1. Ustawienia → Prywatność i ochrona → Kalendarze (NIE „Pełny dostęp do dysku”)"
echo "  2. Włącz Python / python3.13 / uv — cokolwiek się pojawi po teście"
echo "  3. Jeśli lista pusta: wyłącz i włącz ponownie, potem uruchom ten skrypt jeszcze raz"
echo "  4. Nie uruchamiaj tego przez SSH z M5 — dialog TCC wymaga sesji GUI na M1"
echo ""
exit "${RC:-1}"
