<link rel="stylesheet" href="../styles/main.css">

# Runbook — harmonogram sync Knowledge (dev Qdrant)

[← Workspace MVP](../architecture/workspace-mvp.md) · [M5.2 RAG scale](../planning/workspace-mvp-m5-2-rag-scale.md)

**Cel:** manifest T1 i Qdrant `:6335` aktualne bez ręcznego `embed-knowledge sync --dev`.

**Dotyczy:** macOS dev (M5), kolekcja `knowledge_chunks_dev` — **nigdy** prod w tej fazie.

---

## 1. Ręczny sync (baseline)

```bash
cd octadecimal.pro
./scripts/octa-qdrant-dev.sh
./scripts/octa-knowledge-sync-dev.sh
```

Log: `~/.octa/logs/embed-sync.log`

Podgląd bez zapisu:

```bash
OCTA_SYNC_DRY_RUN=1 ./scripts/octa-knowledge-sync-dev.sh
```

---

## 2. macOS launchd (co 6 h)

```bash
chmod +x scripts/octa-knowledge-sync-dev.sh scripts/install-embed-knowledge-launchd.sh
./scripts/install-embed-knowledge-launchd.sh
```

Plist: `~/Library/LaunchAgents/pl.octadecimal.embed-knowledge-dev.plist` (generowany z szablonu w repo).

Ręczny trigger po zmianie w Knowledge:

```bash
launchctl kickstart -k "gui/$(id -u)/pl.octadecimal.embed-knowledge-dev"
```

Weryfikacja:

```bash
tail -20 ~/.octa/logs/embed-sync.log
curl -s http://127.0.0.1:8042/workspace/health | python3 -m json.tool | grep -E 'documents_indexed|knowledge_last_sync'
```

**Oczekiwany wynik:** wpis `sync complete` w logu; `knowledge_last_sync_at` odświeżone po udanym sync.

Odinstalowanie:

```bash
launchctl bootout "gui/$(id -u)/pl.octadecimal.embed-knowledge-dev"
rm ~/Library/LaunchAgents/pl.octadecimal.embed-knowledge-dev.plist
```

---

## 3. Linux / cron (opcjonalnie)

```cron
# co 6 godzin — dostosuj ścieżkę do repo
0 */6 * * * /bin/bash /path/to/octadecimal.pro/scripts/octa-knowledge-sync-dev.sh
```

Wymaga: `uv` w `PATH`, Docker dla Qdrant dev, `KNOWLEDGE_ROOT` ustawione jeśli nie domyślne.

---

## 4. Bezpieczeństwo

Skrypt `octa-knowledge-sync-dev.sh` **odmawia** sync gdy:

- `QDRANT_COLLECTION` ≠ `knowledge_chunks_dev`
- `QDRANT_URL` nie wskazuje lokalnego `:6335`

Nie instaluj tego agenta na serwerze prod — M5.5 wprowadzi osobny target `--prod`.

---

## 5. Troubleshooting

| Objaw | Działanie |
|-------|-----------|
| `uv not found in PATH` | Dodaj Homebrew/`~/.local/bin` do PATH w plist lub uruchamiaj z terminala |
| `failed to start Qdrant dev` | `docker ps`, `./scripts/octa-qdrant-dev.sh` ręcznie |
| Sync OK, UI stare wyniki | Workspace z `RAG_BACKEND=qdrant` musi widzieć tę samą kolekcję |
| Brak pliku w wynikach | `uv run python scripts/embed-knowledge.py scan --dev` — sprawdź `policy.yaml` exclude |
