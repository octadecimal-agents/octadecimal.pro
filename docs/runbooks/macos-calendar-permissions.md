<link rel="stylesheet" href="../styles/main.css">

# Runbook — macOS calendar permissions (Workspace MVP)

[← Workspace MVP](../architecture/workspace-mvp.md) · [M1 server mode](workspace-m1-server-mode.md)

**Goal:** `#Planning` shows live or synced calendar events (`source=macos` or `cache`), not `fixture-denied`.

---

## 1. Architecture (M1 headless)

| Process | launchd | `CALENDAR_PROVIDER` | Role |
|---------|---------|---------------------|------|
| Workspace API | LaunchDaemon | `cache` | Reads `~/.octa/calendar-cache.json` only |
| Calendar sync | LaunchAgent | `macos` | Writes cache from EventKit (hourly + login) |

**Why:** LaunchDaemon cannot reliably use EventKit/TCC. Splitting sync into LaunchAgent + cache avoids manual Privacy clicking after one automated install.

---

## 2. M1 — automated install (recommended)

**One-time on M1 (admin, ~1 min):**

```bash
cd ~/Developer/Repositories/octadecimal-agents/octadecimal.pro
sudo ./scripts/install-m1-calendar-automation.sh
```

**From M5:**

```bash
./scripts/install-m1-calendar-automation.sh --remote m1-admin
```

Installs:

1. **PPPC profile** — pre-grants **Calendars** to the Python binary used by `uv`
2. **LaunchAgent** `pl.octadecimal.calendar-sync-m1` — hourly sync
3. First sync attempt

Then restart Workspace:

```bash
sudo launchctl kickstart -k system/pl.octadecimal.workspace-api-m1-server
```

Verify from M5:

```bash
./scripts/octa workspace smoke --remote m1-ceo --strict-calendar
```

Pass = `calendar_source=cache` (fresh) or `macos`.

Uninstall PPPC: System Settings → Profiles → remove **Octa M1 Calendar**.  
Uninstall sync agent: `./scripts/install-calendar-sync-m1-launchd.sh --uninstall`

---

## 3. M5 / dev (Terminal) — manual

1. **System Settings** → **Privacy & Security** → **Calendars** (PL: **Kalendarze**).
2. Enable **Terminal** / **Cursor** / **iTerm** (whichever starts the server).
3. Not the same as **Full Disk Access** — different pane.

```bash
./scripts/octa-mvp-up.sh
open http://127.0.0.1:8042/#Planning
```

---

## 4. Smoke test (CLI)

```bash
cd octadecimal.pro
export CALENDAR_PROVIDER=auto
uv run python -c "
import asyncio
from secure_agentic_ai.infrastructure.workspace.config import WorkspaceConfig
from secure_agentic_ai.infrastructure.macos.calendar_provider import list_today_calendar_events

async def main():
    config = WorkspaceConfig.from_env()
    events, source = await list_today_calendar_events(config)
    print(f'source={source} events={len(events)}')

asyncio.run(main())
"
```

---

## 5. `calendar_source` values

| Value | Meaning |
|-------|---------|
| `macos` | Live EventKit read |
| `cache` | Sync agent wrote cache today (OK for M1 headless) |
| `fixture` / `fixture-denied` | Fallback — run `install-m1-calendar-automation.sh` on M1 |

---

## 6. Related

- [M1 server runbook](workspace-m1-server-mode.md)
- [CEO checklist M5.6](workspace-m5-6-ceo-checklist.md)
- Legacy manual bootstrap: `scripts/octa-calendar-permission-bootstrap.sh` (superseded by §2)
