# Octa Workspace — Playwright E2E

Browser tests for the Workspace MVP (`http://127.0.0.1:18042` by default). Contract for **backend-team** and **frontend-team**: selector anchors in `tests/workspace.spec.ts` must stay green on every PR — see [dual-track doc](../docs/planning/workspace-mvp-dual-track.md#53-kontrakt-selektorów-e2e-anchors).

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

## Scenarios (12)

1. Boot — greeting + Knowledge index health message
2. `#Wiki` navigation
3. Wiki search — `backup Qdrant` → `Backup.md`
4. Chat — backup question → Kanon + `#Wiki` suggestion
5. `#Board` — create task
6. `#Board` — Octa-native teams (`platform`, `knowledge`, `ops`, `product`) in select + badge
7. `GET /workspace/health` — status, RAG/LLM/calendar fields, pending review count
8. `#Planning` — calendar fixture + generate plan
9. `#Review` — pending HITL queue from `seed_demo.py`
10. Chat — „Co wymaga uwagi?” → Review summary
11. `#Retro` — journal save + preview
12. `#Review` — approve + reject remove items from queue

## Options

```bash
npm run test:headed   # visible browser
npm run test:ui       # Playwright UI mode
E2E_SKIP_SERVER=1 npm test   # reuse server already on :18042
E2E_BASE_URL=http://127.0.0.1:8042 E2E_SKIP_SERVER=1 npm test
```
