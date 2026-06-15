<link rel="stylesheet" href="../styles/main.css">

# Octa Workspace MVP — zamknięte prace (indeks)

[← Workspace MVP roadmap](workspace-mvp-roadmap.md) · [Workspace MVP (EN)](../architecture/workspace-mvp.md)

**Status:** ✅ ukończone · **2026-06-14** · Sprint 0–3 + rozszerzenia + E2E

Ten indeks opisuje **co zostało zbudowane** przed fazą M5.1. Każdy sprint ma osobny plik z architekturą, zrealizowanymi krokami i dowodami weryfikacji — w tym samym formacie co plany faz M5.x.

---

## Mapa zamkniętych sprintów

| Sprint | Cel | Dokument | Commity (główne) |
|--------|-----|----------|------------------|
| [Sprint 0](workspace-mvp-sprint-0-boot.md) | Boot loop, ledger, seed, pierwszy RAG | [workspace-mvp-sprint-0-boot.md](workspace-mvp-sprint-0-boot.md) | `4e58358`, `2526053` |
| [Sprint 1](workspace-mvp-sprint-1-chat-wiki.md) | UI hash, chat AO, Wiki, tryb dry | [workspace-mvp-sprint-1-chat-wiki.md](workspace-mvp-sprint-1-chat-wiki.md) | `4e58358`, `2526053` |
| [Sprint 2](workspace-mvp-sprint-2-panels-hitl.md) | Board, Planning, Review, chat agregacje | [workspace-mvp-sprint-2-panels-hitl.md](workspace-mvp-sprint-2-panels-hitl.md) | `2526053`, `d0f219b` |
| [Sprint 3](workspace-mvp-sprint-3-retro-infra.md) | Retro, Qdrant, kalendarz fixture | [workspace-mvp-sprint-3-retro-infra.md](workspace-mvp-sprint-3-retro-infra.md) | `2526053`, `b10f7bf`, `cafaae4` |
| [Rozszerzenia](workspace-mvp-done-extensions.md) | LLM, sync, MCP, E2E, poprawki | [workspace-mvp-done-extensions.md](workspace-mvp-done-extensions.md) | `820c492`–`9b6e3a7` |

---

## Architektura dostarczonego MVP (bird's eye)

```text
Browser :8042
    │
    ├── GET  /                    index.html + static (app.js, styles.css)
    ├── GET  /workspace/health    RAG + LLM + review_pending_count
    ├── POST /workspace/chat      WorkspaceAgent
    ├── *    /workspace/board/*   WorkspaceLedger (SQLite)
    ├── *    /workspace/planning/*
    ├── *    /workspace/wiki/*
    ├── *    /workspace/review/*  → SqlAlchemyApprovalRequestRepository
    ├── *    /workspace/retro/*
    ├── /operator/*               istniejące HITL console
    └── /actions                  istniejące policy API

Lifespan (app.py):
    init_db() → init_workspace_state()
        ├── WorkspaceLedger + seed demo tasks
        ├── InMemoryVectorStore | QdrantVectorStore
        ├── ingest_knowledge_paths (T1 globs)
        └── build_chat_provider (dry | minimax | deepseek)
```

**Zasada:** Workspace **nie duplikuje** HITL — review korzysta z tej samej bazy approvals co `/operator/`.

---

## Podsumowanie efektów (tabela roadmapy)

| Obszar | Moduły | Weryfikacja |
|--------|--------|-------------|
| Boot loop | `octa-mvp-up.sh`, `app.py` | curl `:8042` → 200 |
| UI hash | `static/index.html`, `app.js` | Playwright nawigacja |
| Chat AO | `workspace_agent.py`, LLM factory | pytest + E2E + MiniMax smoke |
| Wiki | `hybrid_search.py`, `/wiki/search` | E2E `Backup.md` |
| Board | `ledger.py`, router board routes | E2E CRUD + restart |
| Planning | `planning_service.py`, calendar provider | E2E generate plan |
| Review HITL | `review_queue.py`, `review_adapter.py` | E2E + badge |
| Retro | router retro, journal path | E2E journal preview |
| RAG dev | `knowledge_sync.py`, `embed-knowledge.py` | manifest + Qdrant :6335 |
| MCP stub | `workspace_server.py` | `test_workspace_mcp` |
| Testy | pytest 110, Playwright 9 | CI pytest; E2E lokalnie |

---

## Checklist Kanonu (§10) — stan

| Punkt Kanonu | Status | Uwagi |
|--------------|--------|-------|
| Chat + 5 paneli bez błędów JS | ✅ | E2E + fix `loadReview` |
| AO cytuje Knowledge | ✅ | hybrid search + RAG |
| `#Board` CRUD | ✅ | select status (nie drag) |
| `#Review` approve/reject | ✅ | + badge + attention chat |
| `#Retro` journal | ✅ | `{KNOWLEDGE_ROOT}/02-6-Rooms-Model/_system/journal/` |
| Restart — dane Board/plan | ✅ | ledger SQLite |
| pytest zielone | ✅ | 112 testów + CI |
| Playwright E2E | ✅ | 9 scenariuszy w CI |
| `#Zasady` | ✅ | M5.1.4 — statyczne linki |
| Nowy dev < 15 min | ✅ | README quick start (M5.1.6) |

Formalny sign-off → [workspace-mvp-m5-1-signoff.md](workspace-mvp-m5-1-signoff.md)

---

## Definition of Done (zrealizowane)

Każdy zamknięty sprint spełnił:

1. Kod w `src/secure_agentic_ai/` + skrypty w `scripts/`.
2. Testy unit/integration (pytest).
3. Dokumentacja EN: [workspace-mvp.md](../architecture/workspace-mvp.md).
4. Commit(y) na `main` z opisem „why”.

---

## Powiązane dokumenty

- [Sprint 0 — Boot](workspace-mvp-sprint-0-boot.md)
- [Sprint 1 — Chat + Wiki](workspace-mvp-sprint-1-chat-wiki.md)
- [Sprint 2 — Board, Planning, Review](workspace-mvp-sprint-2-panels-hitl.md)
- [Sprint 3 — Retro + infra](workspace-mvp-sprint-3-retro-infra.md)
- [Rozszerzenia po Sprint 3](workspace-mvp-done-extensions.md)
- [Plan dalszych prac M5.x](workspace-mvp-roadmap.md)
