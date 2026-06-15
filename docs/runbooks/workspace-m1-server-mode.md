<link rel="stylesheet" href="../styles/main.css">

# Runbook — Octa Workspace M1 server mode

[← Workspace MVP](../architecture/workspace-mvp.md) · [M5.6 plan](../planning/workspace-mvp-m5-6-m1-server-mode.md) · [M5 daily dev](workspace-daily-dev.md) · [Calendar permissions](macos-calendar-permissions.md)

**Goal:** Workspace API + UI **always-on** on **M1** (daily-driver Mac) at `http://127.0.0.1:8042/` — no manual `./scripts/octa-mvp-up.sh` for routine CEO use.

**Owner:** backend-team · **Scope:** M1 localhost only — no public HTTPS (see [M5.7](../planning/workspace-mvp-m5-7-hosting-only.md)).

---

## 1. Node roles

| Node | Role | launchd label |
|------|------|---------------|
| **M1** | Daily driver — **server mode** (this runbook) | `pl.octadecimal.workspace-api-m1` |
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

## 3. Install (M5.6.1)

On **M1**:

```bash
cd octadecimal.pro
chmod +x scripts/install-workspace-api-m1-launchd.sh scripts/octa-workspace-api-m1.sh
./scripts/install-workspace-api-m1-launchd.sh
```

The installer:

1. Runs `uv sync`
2. Seeds demo data once (`--seed-only`)
3. Installs `~/Library/LaunchAgents/pl.octadecimal.workspace-api-m1.plist`
4. Starts the agent via `launchctl`

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
launchctl kickstart -k "gui/$(id -u)/pl.octadecimal.workspace-api-m1"
```

---

## 4. Verify

```bash
curl -s http://127.0.0.1:8042/workspace/health | python3 -m json.tool
launchctl print "gui/$(id -u)/pl.octadecimal.workspace-api-m1" | head -20
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

**Open UI (M5.6.4 one-liner):**

```bash
open http://127.0.0.1:8042/
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
| `install-workspace-api-m1-launchd.sh` | Install / `--uninstall` |
| `octa-workspace-api-dev.sh` | Core uvicorn startup (shared) |
| `octa-workspace-env.sh` | Shared env + Keychain BWS |
| `install-workspace-api-launchd.sh` | **M5 dev** launchd (not M1) |

---

## 12. Phase checklist (M5.6)

- [x] M5.6.1 — M1 launchd stack
- [x] M5.6.2 — network binding documented (this runbook §6)
- [x] M5.6.3 — `CALENDAR_PROVIDER=auto` in M1 plist
- [x] M5.6.5 — M5/M1 failover documented (§7)
- [ ] M5.6.4 — Shortcuts / CLI wrapper (optional; `open` one-liner above)
- [ ] 3-day smoke (calendar + chat) — operator sign-off on physical M1
