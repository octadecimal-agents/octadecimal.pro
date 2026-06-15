<link rel="stylesheet" href="../styles/main.css">

# Runbook — Knowledge sync M5 → M1

[← Workspace MVP](../architecture/workspace-mvp.md) · [M1 server mode](workspace-m1-server-mode.md) · [Embed sync schedule](knowledge-embed-sync-schedule.md)

**Goal:** keep `~/Developer/Knowledge` on **M1** aligned with **M5** (SSOT) — for Firefox docs, RAG file reads, and CEO offline access.

**Scope:** LAN rsync over SSH (`m1-ceo`). **No** public exposure. **No** `--delete` by default.

---

## 1. Architecture

```text
M5 (SSOT)                          M1 (ceo)
~/Developer/Knowledge  ──rsync──►  ~/Developer/Knowledge
        │                                   │
        │ WatchPaths (launchd)              └── Firefox file:// docs
        └── embed sync → Qdrant :6335 (separate job)
```

| Job | Trigger | Purpose |
|-----|---------|---------|
| `pl.octadecimal.knowledge-sync-m1` | File change in Knowledge + login | Push files to M1 |
| `pl.octadecimal.embed-knowledge-dev` | Every 6 h | Qdrant embed on **M5** only |

These are **independent** — M1 MVP uses `RAG_BACKEND=memory`; file sync is for documentation and future Qdrant on M1.

---

## 2. Manual sync

```bash
cd octadecimal.pro
chmod +x scripts/octa-knowledge-sync-m1.sh
./scripts/octa-knowledge-sync-m1.sh
```

Dry run:

```bash
OCTA_KNOWLEDGE_M1_DRY_RUN=1 ./scripts/octa-knowledge-sync-m1.sh
```

Log: `~/.octa/logs/knowledge-sync-m1.log`

**Requires:** `ssh-add ~/.ssh/m1_ceo_ed25519` (once per M5 session) or Keychain-loaded key.

---

## 3. Automatic sync (launchd on M5)

```bash
chmod +x scripts/install-knowledge-sync-m1-launchd.sh
./scripts/install-knowledge-sync-m1-launchd.sh
```

Plist: `~/Library/LaunchAgents/pl.octadecimal.knowledge-sync-m1.plist`

| Mechanism | Behaviour |
|-----------|-----------|
| `WatchPaths` | Fires when anything under `~/Developer/Knowledge` changes |
| `ThrottleInterval` | Max one rsync per **120 s** (debounce bulk saves) |
| `RunAtLoad` | Sync on M5 login |
| Lock file | Skip if previous rsync still running |

Manual trigger after edits:

```bash
launchctl kickstart -k "gui/$(id -u)/pl.octadecimal.knowledge-sync-m1"
```

Uninstall:

```bash
./scripts/install-knowledge-sync-m1-launchd.sh --uninstall
```

---

## 4. Verify

**On M5:**

```bash
tail -20 ~/.octa/logs/knowledge-sync-m1.log
```

**On M1:**

```bash
ssh m1-ceo 'cat ~/Developer/Knowledge/.octa-sync/last-rsync-from-m5.txt'
ssh m1-ceo 'ls ~/Developer/Knowledge/02-6-Rooms-Model/Operacje/m1/'
```

---

## 5. Excludes (always)

| Path | Reason |
|------|--------|
| `.secrets/` | credentials |
| `.knowledge-index/` | M5 embed manifest (M5-local) |
| `.git/` | size; M1 is read-only mirror |
| `.cursor/` | editor state |

**Mirror mode** (delete orphans on M1 — use with care):

```bash
OCTA_KNOWLEDGE_M1_MIRROR=1 ./scripts/octa-knowledge-sync-m1.sh
```

---

## 6. Troubleshooting

| Symptom | Fix |
|---------|-----|
| `SSH to m1-ceo failed` | `ssh-add ~/.ssh/m1_ceo_ed25519`; check M1 on LAN |
| `skip — another sync in progress` | Wait or remove stale `~/.octa/locks/knowledge-sync-m1/.lock` |
| M1 headless, sync fails | M1 must be awake on AC; SSH Remote Login ON |
| WatchPaths silent | `launchctl kickstart -k …` or re-login on M5 |

---

## 7. Knowledge doc (PL)

Admin guide: `Knowledge/02-6-Rooms-Model/Operacje/m1/Administrator-M1.md` §9.
