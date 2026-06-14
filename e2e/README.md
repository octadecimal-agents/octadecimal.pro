# Octa Workspace — Playwright E2E

Browser tests for the Workspace MVP (`http://127.0.0.1:18042` by default).

## Prerequisites

- [uv](https://docs.astral.sh/uv/) with project deps installed (`uv sync`)
- Node.js 20+

## Run

```bash
cd e2e
npm install   # installs @playwright/test + Chromium into .playwright-browsers/
npm test
```

Playwright starts an isolated API server via `scripts/octa-e2e-server.sh`:

| Variable | E2E value |
|----------|-----------|
| `LLM_PROVIDER` | `dry` (no external LLM) |
| `RAG_BACKEND` | `memory` |
| `CALENDAR_PROVIDER` | `fixture` |
| `DATABASE_URL` | `data/e2e-playwright.db` (fresh seed each run) |
| `KNOWLEDGE_ROOT` | `e2e/.data/knowledge` (includes `Backup.md`) |

## Scenarios (9)

1. Boot — greeting + Knowledge index health message
2. `#Wiki` navigation
3. Wiki search — `backup Qdrant` → `Backup.md`
4. Chat — backup question → Kanon + `#Wiki` suggestion
5. `#Board` — create task
6. `#Planning` — calendar fixture + generate plan
7. `#Review` — pending HITL queue from `seed_demo.py`
8. Chat — „Co wymaga uwagi?” → Review summary
9. `#Retro` — journal save + preview

## Options

```bash
npm run test:headed   # visible browser
npm run test:ui       # Playwright UI mode
E2E_SKIP_SERVER=1 npm test   # reuse server already on :18042
E2E_BASE_URL=http://127.0.0.1:8042 E2E_SKIP_SERVER=1 npm test
```
