<link rel="stylesheet" href="../styles/main.css">

# Runbook — macOS calendar permissions (Workspace MVP)

[← Workspace MVP](../architecture/workspace-mvp.md) · [M5.1 Hardening](../planning/workspace-mvp-m5-1-hardening.md)

**Goal:** `#Planning` shows live EventKit events (`source=macos`) instead of fixture/cache.

**Scope:** M5, `CALENDAR_PROVIDER=auto` (default), `calctl` binary (Darwin dependency in `pyproject.toml`).

---

## 1. Prerequisites

- macOS with **Calendars** app (EventKit)
- Repo `octadecimal.pro` — `uv sync` on Mac (installs `calctl`)
- Terminal, Cursor, iTerm, or the app **from which you run** `./scripts/octa-mvp-up.sh`

---

## 2. Grant Calendars access

1. Open **System Settings** → **Privacy & Security** → **Calendars**.
2. Enable access for the app that starts the server:
   - **Terminal** (default flow)
   - **Cursor** (if starting from integrated terminal)
   - **iTerm** (if using iTerm)
3. If the app is not listed — run `./scripts/octa-mvp-up.sh` once; macOS should prompt. If denied, add manually in Settings.

Optional calendar filter:

```bash
export CALENDAR_INCLUDE=Home,Work,Planning
export CALENDAR_EXCLUDE=Holidays
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

**Expected:** `source=macos` and at least one event (if calendar is not empty).

---

## 4. UI verification

```bash
./scripts/octa-mvp-up.sh
open http://127.0.0.1:8042/#Planning
```

In **Plan dnia** panel check line `Źródło kalendarza: macos` (UI label remains PL for CEO).

Alternatively:

```bash
curl -s http://127.0.0.1:8042/workspace/planning/calendar | python3 -m json.tool
curl -s http://127.0.0.1:8042/workspace/health | python3 -m json.tool
```

Fields `calendar_provider` and `calendar_source` in `/workspace/health` should show `auto` / `macos`.

---

## 5. Cache and fallback

| `calendar_source` | Meaning |
|-------------------|---------|
| `macos` | Live EventKit read |
| `cache` | Last successful read from `~/.octa/calendar-cache.json` |
| `fixture` / `fixture-*` | Static list (no permission or `CALENDAR_PROVIDER=fixture`) |

Cache is written automatically after successful macOS read:

```bash
cat ~/.octa/calendar-cache.json
```

---

## 6. Troubleshooting

| Symptom | Cause | Action |
|---------|-------|--------|
| `source=fixture-denied` | Missing Calendars permission | Settings → enable Terminal/Cursor |
| `source=cache` | Previous read OK, today no access | Fix permissions; delete cache for clean test |
| `source=fixture` | `CALENDAR_PROVIDER=fixture` or missing `calctl` | Expected on Linux/CI; on Mac: `uv sync` |
| Empty calendar | `CALENDAR_INCLUDE` too narrow | Check calendar names in Calendar app |

---

## 7. MCP (Cursor)

Cursor Agent can read the same calendar as `#Planning` via MCP:

```bash
./scripts/octa-mcp-workspace.sh   # stdio — config in docs/architecture/mcp-workspace.example.json
```

**Requirement:** Cursor needs **Calendars** permission (like Terminal) for `CALENDAR_PROVIDER=auto` to return `source=macos`.

Read-only tools: `list_today_calendar`, `wiki_search`, `board_list_tasks`, `review_pending_summary`, `workspace_health`.

---

## Related

- [Workspace MVP — macOS calendar](../architecture/workspace-mvp.md#macos-calendar-mcp-stub)
- [M5.4 — macOS MCP](../planning/workspace-mvp-m5-4-macos-mcp.md)
