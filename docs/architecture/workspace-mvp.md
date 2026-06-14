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
| `LLM_PROVIDER` | `dry` | `dry` (heuristics) or `deepseek` |
| `DEEPSEEK_MODEL` | `deepseek-v4-flash` | DeepSeek V4 model id |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com` | OpenAI-compatible API base |
| `DEEPSEEK_API_KEY` | — | Direct key (dev); prefer Bitwarden in prod |
| `BWS_ACCESS_TOKEN` | — | Machine account token (`m1-runtime`) for Secrets Manager |
| `BWS_PROJECT_NAME` | `multi-agents-framework-m1` | BSM project with `DEEPSEEK_API_KEY` |
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

### DeepSeek V4 (optional)

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

## Planning

- `POST /workspace/planning/generate` — AO builds daily plan from calendar stub + board tasks
- `#Planning` UI — generate, edit inline, save to ledger

## Verification

```bash
uv run pytest tests/integration/test_workspace_mvp.py tests/unit/infrastructure/test_workspace_ledger.py
curl -s http://127.0.0.1:8042/workspace/health | python3 -m json.tool
```

## Intentionally not implemented

- Production Qdrant sync to pc-ubuntu (dev collection only)
- Gemini / Ollama providers (DeepSeek V4 is the external LLM for MVP)
- macOS MCP live calendar/mail
- Full parity with workspace.octadecimal.pro design system
- External LLM providers (Gemini/Ollama wiring is a follow-up)

## Related docs

- Knowledge plan: `Knowledge/.../octa-os/mvp-localhost-m5.md`
- Contributing: `CONTRIBUTING.md`
