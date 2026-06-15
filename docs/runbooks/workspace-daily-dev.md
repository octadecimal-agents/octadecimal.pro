<link rel="stylesheet" href="../styles/main.css">

# Runbook — Octa Workspace daily dev (M5)

[← Workspace MVP](../architecture/workspace-mvp.md) · [M5.5 dev loop](../planning/workspace-mvp-m5-5-m5-complete.md) · [Knowledge sync](knowledge-embed-sync-schedule.md)

**Goal:** start, verify, and troubleshoot Workspace on `http://127.0.0.1:8042/` every day without guesswork.

**Scope:** M5 localhost only — no prod, no pc-ubuntu (see [ADR 006](../adr/006-m5-only-dev-strategy.md)).

---

## 1. Prerequisites

| Requirement | Check |
|-------------|-------|
| [uv](https://docs.astral.sh/uv/) (Python 3.13) | `uv --version` |
| Repo cloned | `octadecimal.pro` + optional `Knowledge` at `~/Developer/Knowledge` |
| Port 8042 free | `curl -sf http://127.0.0.1:8042/workspace/health` → should fail when stopped |

---

## 2. Manual start (foreground)

Best for active development (logs in terminal, Ctrl+C to stop):

```bash
cd octadecimal.pro
./scripts/octa-mvp-up.sh
```

Open http://127.0.0.1:8042/

**Optional env:**

```bash
export LLM_PROVIDER=minimax          # or dry (default), deepseek
export RAG_BACKEND=qdrant            # requires Docker; auto-starts :6335
export KNOWLEDGE_ROOT=~/Developer/Knowledge
./scripts/octa-mvp-up.sh
```

---

## 3. Always-on start (launchd)

Best for daily CEO use — survives reboot, restarts on crash:

```bash
chmod +x scripts/octa-workspace-api-dev.sh scripts/install-workspace-api-launchd.sh
./scripts/install-workspace-api-launchd.sh
```

**Important:** stop manual `./scripts/octa-mvp-up.sh` before installing — both bind `:8042`.

Verify:

```bash
curl -s http://127.0.0.1:8042/workspace/health | python3 -m json.tool
tail -30 ~/.octa/logs/workspace-api.log
```

Restart:

```bash
launchctl kickstart -k "gui/$(id -u)/pl.octadecimal.workspace-api-dev"
```

Uninstall:

```bash
launchctl bootout "gui/$(id -u)/pl.octadecimal.workspace-api-dev"
rm ~/Library/LaunchAgents/pl.octadecimal.workspace-api-dev.plist
# or: ./scripts/install-workspace-api-launchd.sh --uninstall
```

Logs:

| File | Content |
|------|---------|
| `~/.octa/logs/workspace-api.log` | uvicorn + startup script |
| `~/.octa/logs/workspace-api-launchd.out.log` | launchd stdout |
| `~/.octa/logs/workspace-api-launchd.err.log` | launchd stderr |

---

## 4. Health check (daily)

```bash
curl -s http://127.0.0.1:8042/workspace/health | python3 -m json.tool
```

| Field | Healthy |
|-------|---------|
| `status` | `ok` or `degraded` (see `issues`) |
| `documents_indexed` | > 0 when Knowledge present |
| `llm_provider` | `dry`, `minimax`, etc. |
| `review_pending_count` | any number (badge in UI) |

Quick UI smoke:

```bash
open http://127.0.0.1:8042/#Wiki
open http://127.0.0.1:8042/#Review
```

---

## 5. Knowledge RAG sync (optional)

When `RAG_BACKEND=qdrant`, keep the index fresh:

```bash
./scripts/octa-knowledge-sync-dev.sh
# or install launchd (every 6h): ./scripts/install-embed-knowledge-launchd.sh
```

See [knowledge-embed-sync-schedule.md](knowledge-embed-sync-schedule.md).

---

## 6. Run tests locally (before push)

```bash
uv run pytest
cd e2e && npm ci && npm test
```

CI runs the same gates on every push to `main`.

---

## 7. Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `port already serving /workspace/health` | launchd + manual start conflict | Stop one: `launchctl bootout …` or Ctrl+C manual |
| Wiki/RAG empty | Missing `KNOWLEDGE_ROOT` | Clone Knowledge; export path |
| `documents_indexed: 0` with qdrant | No sync yet | `./scripts/octa-knowledge-sync-dev.sh` |
| Qdrant errors | Docker not running | `./scripts/octa-qdrant-dev.sh` |
| `#Review` badge grows | Old seed duplicates | `uv run python scripts/seed_demo.py --reset` |
| Calendar `source=fixture` | macOS permissions | [macos-calendar-permissions.md](macos-calendar-permissions.md) |
| launchd exits loop | uv missing in PATH | Run `uv sync` manually; check plist PATH |
| LLM unavailable | No token | Use `LLM_PROVIDER=dry` or configure BSM/Keychain |

---

## 8. Script map

| Script | Role |
|--------|------|
| `octa-mvp-up.sh` | Interactive dev (foreground) |
| `octa-workspace-api-dev.sh` | Core startup (manual or launchd) |
| `octa-workspace-env.sh` | Shared env (sourced, not run directly) |
| `install-workspace-api-launchd.sh` | Install always-on agent |
| `install-embed-knowledge-launchd.sh` | Install RAG sync schedule |
| `octa-e2e-server.sh` | Isolated server for Playwright (`:18042`) |

---

## Related

- [Workspace MVP architecture](../architecture/workspace-mvp.md)
- [M5.6 M1 server mode](../planning/workspace-mvp-m5-6-m1-server-mode.md) — [M1 runbook](workspace-m1-server-mode.md)
