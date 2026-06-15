<link rel="stylesheet" href="../styles/main.css">

# Runbook — uprawnienia kalendarza macOS (Workspace MVP)

[← Workspace MVP](../architecture/workspace-mvp.md) · [M5.1 Hardening](../planning/workspace-mvp-m5-1-hardening.md)

**Cel:** `#Planning` pokazuje live wydarzenia z EventKit (`source=macos`) zamiast fixture/cache.

**Dotyczy:** M5, `CALENDAR_PROVIDER=auto` (domyślnie), binarka `calctl` (zależność Darwin w `pyproject.toml`).

---

## 1. Wymagania wstępne

- macOS z dostępem do aplikacji **Calendars** (EventKit)
- Repo `octadecimal.pro` — `uv sync` na Macu (instaluje `calctl`)
- Terminal, Cursor, iTerm lub inna aplikacja, **z której uruchamiasz** `./scripts/octa-mvp-up.sh`

---

## 2. Nadaj uprawnienia Calendars

1. Otwórz **System Settings** → **Privacy & Security** → **Calendars**.
2. Włącz dostęp dla aplikacji, która uruchamia serwer:
   - **Terminal** (domyślny flow)
   - **Cursor** (jeśli startujesz z wbudowanego terminala)
   - **iTerm** (jeśli używasz iTerm)
3. Jeśli aplikacji nie ma na liście — uruchom `./scripts/octa-mvp-up.sh` raz; macOS powinien pokazać prompt. Po odrzuceniu dodaj ręcznie w Settings.

Opcjonalnie filtruj kalendarze:

```bash
export CALENDAR_INCLUDE=Dom,Praca,Ogarnianie
export CALENDAR_EXCLUDE=Święta
```

---

## 3. Smoke test (CLI)

```bash
cd octadecimal.pro
export WORKSPACE_ENABLED=1
export KNOWLEDGE_ROOT="${KNOWLEDGE_ROOT:-$HOME/Developer/Knowledge}"
export CALENDAR_PROVIDER=auto

uv run python -c "
import asyncio
from secure_agentic_ai.infrastructure.workspace.config import WorkspaceConfig
from secure_agentic_ai.infrastructure.macos.calendar_provider import list_today_calendar_events

async def main():
    config = WorkspaceConfig.from_env()
    events, source = await list_today_calendar_events(config)
    print(f'source={source} events={len(events)}')
    for e in events[:5]:
        print(f'  {e.time} {e.title} ({e.calendar or \"-\"})')

asyncio.run(main())
"
```

**Oczekiwany wynik:** `source=macos` i co najmniej jedno wydarzenie (jeśli kalendarz nie jest pusty).

---

## 4. Weryfikacja w UI

```bash
./scripts/octa-mvp-up.sh
open http://127.0.0.1:8042/#Planning
```

W panelu **Plan dnia** sprawdź linię `Źródło kalendarza: macos`.

Alternatywnie:

```bash
curl -s http://127.0.0.1:8042/workspace/planning/calendar | python3 -m json.tool
curl -s http://127.0.0.1:8042/workspace/health | python3 -m json.tool
```

Pola `calendar_provider` i `calendar_source` w `/workspace/health` powinny wskazywać `auto` / `macos`.

---

## 5. Cache i fallback

| `calendar_source` | Znaczenie |
|-------------------|-----------|
| `macos` | Live odczyt EventKit |
| `cache` | Ostatni udany odczyt z `~/.octa/calendar-cache.json` |
| `fixture` / `fixture-*` | Statyczna lista (brak uprawnień lub `CALENDAR_PROVIDER=fixture`) |

Cache zapisuje się automatycznie po udanym odczycie macOS:

```bash
cat ~/.octa/calendar-cache.json
```

---

## 6. Rozwiązywanie problemów

| Objaw | Przyczyna | Działanie |
|-------|-----------|-----------|
| `source=fixture-denied` | Brak uprawnień Calendars | Settings → włącz Terminal/Cursor |
| `source=cache` | Wcześniejszy odczyt OK, dziś brak dostępu | Napraw uprawnienia; usuń cache jeśli testujesz od zera |
| `source=fixture` | `CALENDAR_PROVIDER=fixture` lub brak `calctl` | Na Linux/CI to oczekiwane; na Macu: `uv sync` |
| Pusty kalendarz | Filtr `CALENDAR_INCLUDE` zbyt wąski | Sprawdź nazwy kalendarzy w aplikacji Calendar |

---

## Powiązane

- [Workspace MVP — macOS calendar](../architecture/workspace-mvp.md#macos-calendar-mcp-stub)
- [M5.4 — pełny MCP macOS](../planning/workspace-mvp-m5-4-macos-mcp.md)
