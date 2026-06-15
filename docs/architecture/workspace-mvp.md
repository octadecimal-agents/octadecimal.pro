# Octa Workspace MVP (localhost)

Local CEO workspace prototype: chat with the Personal Agent (AO), hash panels, Knowledge RAG, HITL review queue, and SQLite task board.

## Purpose

Implements the loop described in the Octa OS research doc *Typical CEO workday* without production HYDRA, Twenty CRM, or cloud Workspace. The kernel remains `octadecimal.pro` (policy, HITL, audit); Workspace is a thin adapter plus static UI.

## Quick start (M5)

```bash
cd octadecimal.pro
./scripts/octa-mvp-up.sh
```

Open http://127.0.0.1:8042/

| URL | Role |
|-----|------|
| `/` | Workspace UI (chat + hash panels) |
| `/workspace/health` | MVP health + indexed document count |
| `/operator/` | HITL operator console (same process) |

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `WORKSPACE_ENABLED` | `0` | Set to `1` to mount Workspace routes and static UI |
| `KNOWLEDGE_ROOT` | `~/Developer/Knowledge` | Canonical Markdown root |
| `OCTA_LEDGER` | `~/.octa/ledger.sqlite` | Board + planning ledger |
| `LLM_PROVIDER` | `dry` | `dry` (heuristics), `minimax`, or `deepseek` |
| `MINIMAX_MODEL` | `MiniMax-M3` | MiniMax model id (OpenAI-compatible API) |
| `MINIMAX_BASE_URL` | `https://api.minimax.io/v1` | MiniMax API base |
| `MINIMAX_API_TOKEN` | — | Direct token (dev); prefer Bitwarden in prod |
| `BWS_MINIMAX_SECRET_KEY` | `MINIMAX_API_TOKEN` | Secret key name inside the BSM project |
| `MINIMAX_BW_LABEL` | `octadecimal-infra/minimax-api-token` | Fallback: Bitwarden vault label via `Knowledge/tools/bitwarden` |
| `BW_SECRET_ID_MINIMAX_API_TOKEN` | — | Fallback: BSM secret UUID |
| `DEEPSEEK_MODEL` | `deepseek-v4-flash` | DeepSeek V4 model id (legacy) |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com` | OpenAI-compatible API base |
| `DEEPSEEK_API_KEY` | — | Direct key (dev); prefer Bitwarden in prod |
| `BWS_ACCESS_TOKEN` | — | Machine account token (`m1-runtime`) for Secrets Manager |
| `BWS_PROJECT_NAME` | `multi-agents-framework-m1` | BSM project with `MINIMAX_API_TOKEN` (or `DEEPSEEK_API_KEY`) |
| `BWS_DEEPSEEK_SECRET_KEY` | `DEEPSEEK_API_KEY` | Secret key name inside the project |
| `DEEPSEEK_BW_LABEL` | `octadecimal-infra/deepseek-api-key` | Fallback: Bitwarden vault label via `Knowledge/tools/bitwarden` |
| `BW_SECRET_ID_DEEPSEEK_API_KEY` | — | Fallback: BSM secret UUID |
| `RAG_BACKEND` | `memory` | `memory` (in-process) or `qdrant` |
| `QDRANT_URL` | `http://127.0.0.1:6335` | Qdrant REST when `RAG_BACKEND=qdrant` |
| `QDRANT_COLLECTION` | `knowledge_chunks_dev` | Collection name for Knowledge chunks |
| `OCTA_REINDEX` | `0` | Set to `1` to force re-ingest on startup |

### Qdrant dev (optional)

```bash
./scripts/octa-qdrant-dev.sh          # Docker on :6335
export RAG_BACKEND=qdrant
./scripts/octa-mvp-up.sh              # auto-starts Qdrant when backend=qdrant
```

Or start Qdrant manually:

```bash
docker compose -f docker-compose.qdrant-dev.yml up -d
```

Incremental sync (only changed T1 files):

```bash
./scripts/octa-qdrant-dev.sh
uv run python scripts/embed-knowledge.py scan --dev    # count T1 files (policy.yaml)
uv run python scripts/embed-knowledge.py sync --dev
uv run python scripts/embed-knowledge.py sync --dev --dry-run   # preview diff
```

With `policy.yaml` in place, a typical local Knowledge tree indexes **~80+** T1 markdown files (expect `documents_indexed` >> 77 in `/workspace/health` after ingest).

Manifest: `KNOWLEDGE_ROOT/.knowledge-index/manifest-dev.json`. Workspace startup skips full ingest when the Qdrant collection already has points (`OCTA_REINDEX=1` forces rebuild).

**Embed policy:** `KNOWLEDGE_ROOT/.knowledge-index/policy.yaml` defines tier T1 include/exclude globs (see [knowledge-policy.example.yaml](knowledge-policy.example.yaml)). When missing, code falls back to built-in `knowledge_globs` in `WorkspaceConfig`.

**Retrieval debug (dev):** set `WORKSPACE_DEBUG=1` and pass header `X-Debug-Retrieval: 1` on `/workspace/wiki/search` to include `vector_score`, `keyword_score`, and `keyword_raw` per hit. Structured JSON logs go to logger `secure_agentic_ai.retrieval`.

### MiniMax (recommended external LLM)

```bash
# Machine account m1-runtime (Bitwarden Secrets Manager)
export BWS_ACCESS_TOKEN="..."   # token — Keychain, nie repo
export LLM_PROVIDER=minimax
export RAG_BACKEND=qdrant
./scripts/octa-mvp-up.sh
```

Key resolution order: `MINIMAX_API_TOKEN` / `MINIMAX_API_KEY` → `BWS_ACCESS_TOKEN` + project `multi-agents-framework-m1` / key `MINIMAX_API_TOKEN` → `BW_SECRET_ID_*` → Bitwarden vault (`bw`).
If no token is found, AO falls back to dry mode.

`octa-mvp-up.sh` auto-loads `BWS_ACCESS_TOKEN` from macOS Keychain when present (`pl.octadecimal.m1-runtime.BWS_ACCESS_TOKEN`).

### DeepSeek V4 (legacy)

```bash
# Machine account m1-runtime (Bitwarden Secrets Manager)
export BWS_ACCESS_TOKEN="..."   # token — Keychain, nie repo
export LLM_PROVIDER=deepseek
./scripts/octa-mvp-up.sh
```

Key resolution order: `DEEPSEEK_API_KEY` → `BWS_ACCESS_TOKEN` + project `multi-agents-framework-m1` / key `DEEPSEEK_API_KEY` → `BW_SECRET_ID_*` → Bitwarden vault (`bw`).
If no key is found, AO falls back to dry mode.

## Architecture

```text
Browser → FastAPI :8042
            ├── /static          Workspace UI assets
            ├── /workspace/*     Board, chat, wiki, review, retro API
            ├── /operator/*      Existing HITL console
            └── /actions         Existing policy API
```

Knowledge ingest (MVP): scan T1 globs under `KNOWLEDGE_ROOT`, strip HTML callouts, chunk + embed. Default backend is in-memory (`FakeEmbeddingProvider`, CI-friendly). Set `RAG_BACKEND=qdrant` to persist chunks in local Qdrant on `:6335`. **Hybrid re-ranking** boosts filename/path token matches (e.g. `Backup.md` for “backup Qdrant”).

## Review queue (HITL)

- `GET /workspace/review/pending` — pending CEO approvals (same DB as `/operator/`)
- Sidebar badge on `#Review` shows pending count; refreshed after approve/reject
- AO answers „co wymaga uwagi?” / „review” with queue summary + suggests `#Review`
- `/workspace/health` includes `review_pending_count`, `llm_available`, knowledge manifest age, and calendar source

Example:

```json
{
  "status": "ok",
  "documents_indexed": 251,
  "rag_backend": "memory",
  "llm_provider": "dry",
  "llm_available": false,
  "review_pending_count": 3,
  "knowledge_manifest_age_seconds": 3600,
  "knowledge_last_sync_at": "2026-06-14T10:00:00+00:00",
  "calendar_provider": "auto",
  "calendar_source": "fixture"
}
```

## macOS calendar (MCP stub)

Calendar for `#Planning` uses `CALENDAR_PROVIDER`:

| Value | Behavior |
|-------|----------|
| `auto` (default) | macOS EventKit via `calctl` when permitted, else fixture/cache |
| `macos` | EventKit only; falls back to cache/fixture on error |
| `fixture` | `DEFAULT_CALENDAR` or `~/.octa/calendar-fixture.json` |

```bash
# Grant Calendars permission when macOS prompts (System Settings → Privacy → Calendars)
export CALENDAR_PROVIDER=auto
export CALENDAR_INCLUDE=Dom,Praca,Ogarnianie   # optional filter
./scripts/octa-mcp-workspace.sh                 # Cursor MCP (stdio)
```

MCP tools: `list_today_calendar`, `workspace_health`. Example Cursor config: `docs/architecture/mcp-workspace.example.json`.

Successful macOS reads are cached in `~/.octa/calendar-cache.json` for the current day.

**Runbook (uprawnienia):** [macos-calendar-permissions.md](../runbooks/macos-calendar-permissions.md)

## Planning

- `POST /workspace/planning/generate` — AO builds daily plan from calendar stub + board tasks
- `#Planning` UI — generate, edit inline, save to ledger

## Verification

```bash
uv run pytest tests/integration/test_workspace_mvp.py tests/unit/infrastructure/test_workspace_ledger.py
curl -s http://127.0.0.1:8042/workspace/health | python3 -m json.tool

# Browser E2E (isolated server on :18042, dry LLM + memory RAG)
cd e2e && npm install && npm test
```

See `e2e/README.md` for scenarios and `E2E_SKIP_SERVER` when reusing a running dev instance.

## Intentionally not implemented

- Production Qdrant sync to pc-ubuntu (dev collection only)
- Live Mail/Contacts MCP (calendar stub only for MVP)
- Full parity with workspace.octadecimal.pro design system

## Related docs

- Knowledge plan: `Knowledge/.../octa-os/mvp-localhost-m5.md`
- Next tasks roadmap: [workspace-mvp-roadmap.md](../planning/workspace-mvp-roadmap.md)
- Completed work: [workspace-mvp-done-index.md](../planning/workspace-mvp-done-index.md) (Sprint 0–3)
- Contributing: `CONTRIBUTING.md`
