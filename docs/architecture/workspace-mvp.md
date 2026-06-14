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
| `LLM_PROVIDER` | `dry` | AO replies without external LLM |

## Architecture

```text
Browser → FastAPI :8042
            ├── /static          Workspace UI assets
            ├── /workspace/*     Board, chat, wiki, review, retro API
            ├── /operator/*      Existing HITL console
            └── /actions         Existing policy API
```

Knowledge ingest (MVP): scan T1 globs under `KNOWLEDGE_ROOT`, strip HTML callouts, chunk + embed into in-memory vector store using `FakeEmbeddingProvider` (deterministic, CI-friendly).

## Verification

```bash
uv run pytest tests/integration/test_workspace_mvp.py tests/unit/infrastructure/test_workspace_ledger.py
curl -s http://127.0.0.1:8042/workspace/health | python3 -m json.tool
```

## Intentionally not implemented

- Production Qdrant sync (use `RAG_BACKEND=qdrant` later)
- macOS MCP live calendar/mail
- Full parity with workspace.octadecimal.pro design system
- External LLM providers (Gemini/Ollama wiring is a follow-up)

## Related docs

- Knowledge plan: `Knowledge/.../octa-os/mvp-localhost-m5.md`
- Contributing: `CONTRIBUTING.md`
