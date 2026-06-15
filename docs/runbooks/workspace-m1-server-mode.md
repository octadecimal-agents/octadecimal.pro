<link rel="stylesheet" href="../styles/main.css">

# Runbook — Octa Workspace M1 server mode

[← Workspace MVP](../architecture/workspace-mvp.md) · [M5.6 plan](../planning/workspace-mvp-m5-6-m1-server-mode.md) · [M5 daily dev](workspace-daily-dev.md) · [Calendar permissions](macos-calendar-permissions.md)

**Goal:** Workspace API + UI **always-on** on **M1** (daily-driver Mac) at `http://127.0.0.1:8042/` — no manual `./scripts/octa-mvp-up.sh` for routine CEO use.

**Owner:** backend-team · **Scope:** M1 localhost only — no public HTTPS (see [M5.7](../planning/workspace-mvp-m5-7-hosting-only.md)).

---

## 1. Node roles

| Node | Role | launchd label |
|------|------|---------------|
| **M1** | Daily driver — **server mode** (this runbook) | `pl.octadecimal.workspace-api-m1-server` (daemon) or `-m1` (agent) |
| **M5** | Dev/build — tests, CI, foreground dev | `pl.octadecimal.workspace-api-dev` |

Only **one** launchd agent may bind `:8042` on a given Mac. Do not install both labels on the same machine.

---

## 2. Prerequisites (M1)

| Requirement | Check |
|-------------|-------|
| macOS on M1 | daily driver |
| [uv](https://docs.astral.sh/uv/) (Python 3.13) | `uv --version` |
| Repo cloned | `octadecimal.pro` at e.g. `~/Developer/Repositories/octadecimal-agents/octadecimal.pro` |
| Knowledge (optional) | `~/Developer/Knowledge` — Wiki/RAG empty without it |
| Port 8042 free | `curl -sf http://127.0.0.1:8042/workspace/health` → fail when stopped |

---

## 2.1 Bootstrap from M5 via SSH

M1 is reachable on LAN as **`M1.local`** (`192.168.0.172`). SSH hosts on M5 (`~/.ssh/config`):

| Host | User | Use |
|------|------|-----|
| `m1-ceo` | CEO | Workspace server mode (this runbook) |
| `m1-admin` | Admin | Console admin on M1 |

```bash
# On M5 — load key once per session (passphrase in Keychain / ssh-add locally)
ssh-add ~/.ssh/m1_ceo_ed25519

# Sync repo to M1 (first time or after big changes)
rsync -az --exclude '.venv' --exclude 'node_modules' --exclude '__pycache__' \
  ~/Developer/Repositories/octadecimal-agents/octadecimal.pro/ \
  m1-ceo:Developer/Repositories/octadecimal-agents/octadecimal.pro/

# Remote install
ssh m1-ceo 'cd ~/Developer/Repositories/octadecimal-agents/octadecimal.pro && ./scripts/install-workspace-api-m1-launchd.sh'
```

**GUI session required for LaunchAgent only.** If `launchctl bootstrap gui/...` fails with **125**, the console user is still `admin` while Workspace runs as `ceo`. Use **LaunchDaemon** (recommended on this fleet):

```bash
# On M1 — as admin (or any user with sudo), from CEO repo path
cd /Users/ceo/Developer/Repositories/octadecimal-agents/octadecimal.pro
sudo ./scripts/install-workspace-api-m1-launchd.sh --daemon
curl -s http://127.0.0.1:8042/workspace/health | python3 -m json.tool
```

LaunchDaemon runs at boot as user `ceo` — no CEO GUI login required.

**LaunchAgent** (only if CEO is the console login):

```bash
# Must show Name: ceo in scutil ConsoleUser
./scripts/install-workspace-api-m1-launchd.sh
```

---

## 3. Install (M5.6.1)

On **M1** — **recommended** when console login is `admin` and Workspace runs as `ceo`:

```bash
cd /Users/ceo/Developer/Repositories/octadecimal-agents/octadecimal.pro
chmod +x scripts/install-workspace-api-m1-launchd.sh scripts/octa-workspace-api-m1.sh
sudo ./scripts/install-workspace-api-m1-launchd.sh --daemon
```

**LaunchAgent** (only if CEO is logged in at the console — `scutil <<< ConsoleUser` shows `Name: ceo`):

```bash
./scripts/install-workspace-api-m1-launchd.sh
```

The installer:

1. Runs `uv sync`
2. Seeds demo data once (`--seed-only`)
3. Installs plist (`LaunchDaemon` → `/Library/LaunchDaemons/…-server.plist`, or `LaunchAgent` → `~/Library/LaunchAgents/…-m1.plist`)
4. Starts the job via `launchctl`

**Defaults in M1 plist:**

| Variable | Value |
|----------|-------|
| `OCTA_NODE` | `m1` |
| `LLM_PROVIDER` | `dry` |
| `RAG_BACKEND` | `memory` |
| `CALENDAR_PROVIDER` | `auto` |
| `WORKSPACE_HOST` | `127.0.0.1` (via startup script guard) |

To use MiniMax on M1: edit the plist `LLM_PROVIDER` → `minimax` after install (requires BSM token in Keychain — see [workspace-mvp.md](../architecture/workspace-mvp.md)). Then:

```bash
# LaunchDaemon (recommended)
sudo launchctl kickstart -k system/pl.octadecimal.workspace-api-m1-server

# LaunchAgent (CEO console only)
launchctl kickstart -k "gui/$(id -u)/pl.octadecimal.workspace-api-m1"
```

---

## 4. Verify

```bash
curl -s http://127.0.0.1:8042/workspace/health | python3 -m json.tool
launchctl print system/pl.octadecimal.workspace-api-m1-server | head -20   # daemon
# launchctl print "gui/$(id -u)/pl.octadecimal.workspace-api-m1" | head -20  # agent
open http://127.0.0.1:8042/
```

Expected health fields: `status` ok/degraded, `calendar_provider` `auto`, `review_pending_count` ≥ 0 after seed.

**After reboot:** repeat `curl` — agent should return without manual start.

---

## 5. Calendar on M1 (M5.6.3)

M1 plist sets `CALENDAR_PROVIDER=auto`. Grant **Calendars** permission when macOS prompts (often on first `#Planning` load or first API calendar read).

See [macos-calendar-permissions.md](macos-calendar-permissions.md). Verify:

```bash
curl -s http://127.0.0.1:8042/workspace/health | python3 -c "import sys,json; h=json.load(sys.stdin); print(h.get('calendar_source'), h.get('calendar_events_count'))"
```

---

## 6. Network binding (M5.6.2)

| Binding | Policy |
|---------|--------|
| `127.0.0.1:8042` | **Default and required** for M1 server mode — local CEO browser only |
| Tailscale LAN | **Not enabled** in MVP — document before exposing; requires explicit ADR + auth |
| Public internet | **Out of scope** until [M5.7](../planning/workspace-mvp-m5-7-hosting-only.md) |

Startup script **refuses** non-localhost `WORKSPACE_HOST` or non-8042 port.

---

## 7. M5 dev vs M1 server — failover (M5.6.5)

| Scenario | Behaviour |
|----------|-----------|
| CEO on M1, launchd running | Use `http://127.0.0.1:8042/` — normal |
| `gui/UID` unavailable on install | User never logged in at console — see §2.1 |
| Developer runs `./scripts/octa-mvp-up.sh` on **same Mac** as M1 launchd | **Conflict** — port 8042 busy; stop launchd first or use another machine |
| Active dev on **M5**, CEO on **M1** | Independent — each Mac has its own `:8042` instance |
| M1 launchd crash | `KeepAlive` restarts; check `~/.octa/logs/workspace-api-m1.log` |
| After `git pull` on M1 | `uv sync` then `launchctl kickstart -k gui/$(id -u)/pl.octadecimal.workspace-api-m1` |

**While developing on M5:** M1 server mode is unaffected (separate machine). Do not point M1 plist at M5 API unless you add a dedicated proxy (out of scope).

---

## 8. Logs

| File | Content |
|------|---------|
| `~/.octa/logs/workspace-api-m1.log` | uvicorn + startup (main) |
| `~/.octa/logs/workspace-api-m1-launchd.out.log` | launchd stdout |
| `~/.octa/logs/workspace-api-m1-launchd.err.log` | launchd stderr |

```bash
tail -f ~/.octa/logs/workspace-api-m1.log
```

---

## 9. Operations

**Restart:**

```bash
launchctl kickstart -k "gui/$(id -u)/pl.octadecimal.workspace-api-m1"
```

**Uninstall:**

```bash
./scripts/install-workspace-api-m1-launchd.sh --uninstall
```

**Open UI (M5.6.4):**

```bash
# From repo (M1 or M5 with local API)
./scripts/octa workspace open

# Or direct script
./scripts/octa-workspace-open.sh

# Optional: add to PATH once
# export PATH="$HOME/Developer/Repositories/octadecimal-agents/octadecimal.pro/scripts:$PATH"
# octa workspace open
```

If API is down, `open` kickstarts LaunchDaemon/LaunchAgent automatically (disable with `--no-kickstart`).

**Smoke check (M5.6 closure):**

```bash
# From M5 — remote checks on M1
./scripts/octa workspace smoke --remote m1-ceo

# On M1 locally
./scripts/octa workspace smoke

# Strict: fail until live EventKit (after Calendars permission)
./scripts/octa workspace smoke --remote m1-ceo --strict-calendar
```

Log 3 consecutive daily passes in [workspace-m5-6-smoke-log.md](workspace-m5-6-smoke-log.md).

**Unattended (CEO nie musi pamiętać):**

```bash
# Jednorazowo: cron 09:00 na M5 + auto-aktualizacja tabeli w smoke-log.md
./scripts/install-m5-m1-smoke-cron.sh

# Ręcznie (np. po deployu)
OCTA_SMOKE_UPDATE_DOC=1 ./scripts/octa-m1-smoke-daily.sh
# Logi: ~/.octa/logs/m5-6-m1-smoke.log · ~/.octa/logs/m5-6-m1-smoke.jsonl
```

---

## 10. Troubleshooting

| Symptom | Fix |
|---------|-----|
| Install refuses: dev launchd loaded | `./scripts/install-workspace-api-launchd.sh --uninstall` (on M5 dev node only) |
| Port 8042 in use | Stop `./scripts/octa-mvp-up.sh` or other launchd label |
| Health 404 / connection refused | `launchctl kickstart -k …`; read `workspace-api-m1.log` |
| Calendar `source=fixture` on M1 | Grant Calendars permission; see calendar runbook |
| `knowledge_root_exists: false` | Clone Knowledge to `~/Developer/Knowledge` or set `KNOWLEDGE_ROOT` in plist |

---

## 11. Related scripts

| Script | Role |
|--------|------|
| `octa-workspace-api-m1.sh` | M1 startup wrapper (launchd + manual) |
| `octa-workspace-open.sh` | M5.6.4 — open UI + optional launchd kickstart |
| `octa-m1-smoke-check.sh` | M5.6 smoke (local or `--remote m1-ceo`) |
| `octa-m1-smoke-daily.sh` | M5.6 unattended daily smoke + log append |
| `install-m5-m1-smoke-cron.sh` | Cron 09:00 on M5 |
| `octa` | CLI dispatcher: `octa workspace open\|smoke` |
| `install-workspace-api-m1-launchd.sh` | Install / `--uninstall` |
| `octa-workspace-api-dev.sh` | Core uvicorn startup (shared) |
| `octa-workspace-env.sh` | Shared env + Keychain BWS |
| `install-knowledge-sync-m1-launchd.sh` | M5 → M1 Knowledge rsync (WatchPaths) |
| `octa-m1-security-audit.sh` | M1 audit report + email |
| `install-m1-security-audit-launchd.sh` | Daily + sudo-triggered audit (M1) |

---

## 12. Phase checklist (M5.6)

- [x] M5.6.1 — M1 launchd stack
- [x] M5.6.2 — network binding documented (this runbook §6)
- [x] M5.6.3 — `CALENDAR_PROVIDER=auto` in M1 plist
- [x] M5.6.5 — M5/M1 failover documented (§7)
- [x] M5.6.4 — `octa workspace open` + smoke script
- [ ] 3-day smoke (calendar + chat) — [smoke log](workspace-m5-6-smoke-log.md)

---

## 13. Headless — closed lid, no monitor, on AC power

**Goal:** M1 stays awake on power with the lid closed; Workspace keeps running; SSH from M5 works for ops/sync. CEO opens the lid later and `http://127.0.0.1:8042/` is already up.

**Reality check:** macOS treats **closed lid + no external display** as a sleep trigger (hall sensor). Energy Saver sliders and `caffeinate` alone are **not enough**. You need **`pmset disablesleep`** and, for reliability, the right **launchd** tier.

### 13.1 Recommended stack (this fleet)

| Layer | Setting | Why |
|-------|---------|-----|
| Power | MacBook **always on AC** | Critical battery still forces sleep despite `disablesleep` |
| Sleep override | `sudo pmset -a disablesleep 1` | Only reliable lid-close veto at kernel level |
| Display trick (optional) | **Dummy HDMI/DP dongle** (~$5) | Without a “display”, macOS may throttle Wi‑Fi/GPU; dongle avoids that |
| Workspace process | **LaunchDaemon** `--daemon` | Survives closed lid; no CEO GUI login required |
| Remote ops | **Remote Login (SSH)** | Manage/sync from M5 when lid is closed |
| Power restore | `sudo pmset -a autorestart 1` | Auto-boot after outage when plugged in |

**LaunchAgent** (current CEO-console install) can work with `disablesleep`, but if the GUI session ends (logout, sleep slip, reboot without auto-login), `:8042` stops until CEO logs in again. For “acts like a server”, prefer **LaunchDaemon**.

### 13.2 One-time setup (on M1)

**A. Remote Login (SSH)** — System Settings → General → Sharing → **Remote Login** ON. Allow user `ceo` (and `admin` if needed).

**B. Workspace as LaunchDaemon** (if not already):

```bash
cd /Users/ceo/Developer/Repositories/octadecimal-agents/octadecimal.pro
# Remove LaunchAgent if you used it before
./scripts/install-workspace-api-m1-launchd.sh --uninstall-agent
sudo ./scripts/install-workspace-api-m1-launchd.sh --daemon
```

**C. Power management** (run as admin with sudo):

```bash
# Prevent sleep (including closed lid) while on AC
sudo pmset -a disablesleep 1

# Server-friendly idle timers (when disablesleep is off again, these still help on AC)
sudo pmset -a sleep 0 displaysleep 0 disksleep 0 standby 0 autopoweroff 0

# Boot automatically when power returns after outage
sudo pmset -a autorestart 1

# Optional: wake for network access (useful if sleep ever re-enabled)
sudo pmset -a womp 1 tcpkeepalive 1

# Inspect
pmset -g custom
pmset -g assertions
```

**D. Auto-login (optional but helps LaunchAgent path):** System Settings → Users & Groups → automatically log in as **ceo**. Skip if you use LaunchDaemon only.

**E. Prevent session logout:** System Settings → Lock Screen — set **Require password** to a long interval or “Never” for the CEO account used as server; disable “Log out after X minutes of inactivity” if present.

**F. Dummy HDMI (recommended without external monitor):** Plug a headless HDMI/DP adapter into M1 before closing the lid. Keeps Wi‑Fi performance stable on many MacBooks.

### 13.3 Going headless (procedure)

1. Confirm health: `curl -s http://127.0.0.1:8042/workspace/health`
2. Confirm SSH from M5: `ssh m1-ceo 'uptime'`
3. Plug **AC adapter** (required)
4. Plug **dummy HDMI** (recommended)
5. Run `sudo pmset -a disablesleep 1` if not persistent
6. **Close the lid**
7. From M5 after ~30s:

```bash
ssh m1-ceo 'pmset -g assertions | head -5; curl -sf http://127.0.0.1:8042/workspace/health | python3 -m json.tool'
```

### 13.4 Verify after reboot (closed-lid server test)

1. Reboot M1 (ceo logged in or LaunchDaemon installed)
2. Wait 2–3 min on AC, lid closed
3. From M5:

```bash
ssh m1-ceo 'launchctl print system/pl.octadecimal.workspace-api-m1-server | grep state'
ssh m1-ceo 'curl -sf http://127.0.0.1:8042/workspace/health'
```

Pass = SSH OK + health `status: ok` without opening the lid.

### 13.5 Revert to normal laptop behaviour

```bash
sudo pmset -a disablesleep 0
sudo pmset -a sleep 10 displaysleep 10 disksleep 10 standby 1 autopoweroff 1
# Unplug dummy HDMI; use Energy Saver defaults in System Settings
```

Menubar tools (Awayke, Amphetamine closed-display mode, StayAwake) wrap the same `pmset disablesleep` if you prefer a toggle over raw CLI.

### 13.6 Limitations (MVP)

| Topic | Note |
|-------|------|
| API binding | Still **`127.0.0.1:8042`** — LAN clients cannot hit Workspace; headless = always-on **local** API + SSH ops |
| Calendar | EventKit may stay on `fixture` until Calendars permission granted; live reads need CEO GUI at least once |
| Battery | Do **not** rely on closed-lid server mode on battery — macOS will sleep |
| Thermal | Closed lid reduces cooling; sustained load + AC is fine for Workspace MVP; avoid heavy GPU jobs in clamshell |
