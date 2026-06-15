<link rel="stylesheet" href="../styles/main.css">

# Runbook — Knowledge embed sync schedule (dev Qdrant)

[← Workspace MVP](../architecture/workspace-mvp.md) · [M5.2 RAG scale](../planning/workspace-mvp-m5-2-rag-scale.md)

**Goal:** keep T1 manifest and Qdrant `:6335` current without manual `embed-knowledge sync --dev`.

**Scope:** macOS dev (M5), collection `knowledge_chunks_dev` — **never** prod in this phase.

---

## 1. Manual sync (baseline)

```bash
cd octadecimal.pro
./scripts/octa-qdrant-dev.sh
./scripts/octa-knowledge-sync-dev.sh
```

Log: `~/.octa/logs/embed-sync.log`

Dry run:

```bash
OCTA_SYNC_DRY_RUN=1 ./scripts/octa-knowledge-sync-dev.sh
```

---

## 2. macOS launchd (every 6 h)

```bash
chmod +x scripts/octa-knowledge-sync-dev.sh scripts/install-embed-knowledge-launchd.sh
./scripts/install-embed-knowledge-launchd.sh
```

Plist: `~/Library/LaunchAgents/pl.octadecimal.embed-knowledge-dev.plist` (generated from repo template).

Manual trigger after Knowledge changes:

```bash
launchctl kickstart -k "gui/$(id -u)/pl.octadecimal.embed-knowledge-dev"
```

Verify:

```bash
tail -20 ~/.octa/logs/embed-sync.log
curl -s http://127.0.0.1:8042/workspace/health | python3 -m json.tool | grep -E 'documents_indexed|knowledge_last_sync'
```

**Expected:** `sync complete` in log; `knowledge_last_sync_at` refreshed after successful sync.

Uninstall:

```bash
launchctl bootout "gui/$(id -u)/pl.octadecimal.embed-knowledge-dev"
rm ~/Library/LaunchAgents/pl.octadecimal.embed-knowledge-dev.plist
```

---

## 3. Linux / cron (optional)

```cron
# every 6 hours — adjust repo path
0 */6 * * * /bin/bash /path/to/octadecimal.pro/scripts/octa-knowledge-sync-dev.sh
```

Requires: `uv` in `PATH`, Docker for dev Qdrant, `KNOWLEDGE_ROOT` if non-default.

---

## 4. Safety

Script `octa-knowledge-sync-dev.sh` **refuses** sync when:

- `QDRANT_COLLECTION` ≠ `knowledge_chunks_dev`
- `QDRANT_URL` does not point to local `:6335`

Do not install this agent on prod server — [M5.7](../planning/workspace-mvp-m5-7-hosting-only.md) introduces separate `--prod` target (deferred).

---

## 5. Troubleshooting

| Symptom | Action |
|---------|--------|
| `uv not found in PATH` | Add Homebrew/`~/.local/bin` to PATH in plist or run from terminal |
| `failed to start Qdrant dev` | `docker ps`, run `./scripts/octa-qdrant-dev.sh` manually |
| Sync OK, stale UI results | Workspace with `RAG_BACKEND=qdrant` must use same collection |
| Missing file in results | `uv run python scripts/embed-knowledge.py scan --dev` — check `policy.yaml` exclude |
