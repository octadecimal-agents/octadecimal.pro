<link rel="stylesheet" href="../styles/main.css">

# Sprint 2 — Planning, Board, Review (zamknięty)

[← Indeks zamkniętych prac](workspace-mvp-done-index.md) · [Sprint 1](workspace-mvp-sprint-1-chat-wiki.md)

**Status:** ✅ done · **2026-06** · commity: `2526053`, `d0f219b`

## Cel sprintu (Kanon)

CRUD tablicy zadań; plan dnia z generacją AO; kolejka HITL w `#Review`; chat agreguje zablokowane taski.

---

## Zrealizowane zadania

| ID | Zadanie | Done when | Status |
|----|---------|-----------|--------|
| 2.1 | CRUD `#Board` | task przetrwa restart | ✅ |
| 2.2 | `#Planning` generacja + edycja | zapis w ledger | ✅ |
| 2.3 | `#Review` approve/reject | akcja znika z kolejki | ✅ |
| 2.4 | Chat „co zablokowane?” | lista teamów | ✅ |

**Rozszerzenie po sprintcie (Review UX):**

| ID | Zadanie | Status |
|----|---------|--------|
| — | Badge `#Review` + „co wymaga uwagi?” | ✅ `d0f219b` |

---

## Architektura Board

### Ledger jako source of truth

```text
GET    /workspace/board/tasks
POST   /workspace/board/tasks        { team, title, intent? }
PATCH  /workspace/board/tasks/{id}   { status, title, ... }
```

**Model:** `Task` dataclass w `ledger.py` — teams: `automation`, `security`, `frontend`, `ux`.

**Statusy:** `todo` | `doing` | `blocked` | `done` — UI: `<select>` na karcie (nie drag-and-drop — świadomy scope cut).

### UI (`app.js`)

- `loadBoard()` — render kart w `#task-list`
- `#add-task-btn` → POST → reload
- Change status → PATCH inline

**Persistence:** `~/.octa/ledger.sqlite` — przetrwa restart uvicorn.

---

## Architektura Planning

### Skład planu dnia

```text
generate_daily_plan(ledger, calendar_events)
    ├── stałe sloty (deep work, review HITL)     planning_service.py
    ├── wydarzenia z kalendarza                  source: calendar
    └── taski blocked z board                    source: board
```

**API:**

| Endpoint | Rola |
|----------|------|
| `GET /planning/items?plan_date=` | lista pozycji |
| `PUT /planning/items` | replace całego planu (edycja CEO) |
| `POST /planning/generate` | AO generuje na dziś |
| `GET /planning/calendar` | wydarzenia + source |

**UI:** `#generate-plan-btn`, edycja inline inputów, `#save-plan-btn`.

**Seed:** `seed_workspace_mvp.py` — 4 pozycje na dziś jeśli pusty.

---

## Architektura Review (HITL)

### Wspólna baza z Operatorem

**Decyzja architektoniczna:** Review w Workspace **nie jest osobnym systemem** — to ten sam `ApprovalRequest` co `/operator/`.

```text
GET  /workspace/review/pending     → ApprovalSummary[]
POST /workspace/review/{id}/approve
POST /workspace/review/{id}/reject
```

Repozytorium: `SqlAlchemyApprovalRequestRepository(session)` — session z `get_db_session()`.

Audit: `SqlAlchemyAuditWriter` — eventy APPROVED/REJECTED z `actor_id=ceo-workspace`.

### Adapter review → AO

`application/review_queue.py`:

- `PendingReviewItem` — DTO dla UI i agenta
- `matches_attention_query()` — „co wymaga uwagi?”
- `format_attention_reply()` — priorytety: Review > blocked board

`infrastructure/workspace/review_adapter.py` — mapowanie domain → DTO.

### UI Review

- `loadReview()` — lista z Approve/Reject (fix składni JS: `async function` w `3ec1e03`)
- `#review-badge` — licznik pending w sidebar
- `refreshReviewBadge()` — po init health + po approve/reject

---

## 2.4 — Chat agregacje

**WorkspaceAgent** — ścieżki deterministyczne (bez LLM):

| Trigger | Odpowiedź | suggested_hash |
|---------|-----------|----------------|
| zablokow / blocked | lista tasków | `#Board` |
| co wymaga uwagi | podsumowanie Review + blocked | `#Review` |
| review / akceptac | lista pending | `#Review` |
| plan / dzisiaj | plan_items z ledger | `#Planning` |

Testy: `tests/unit/application/test_review_queue.py`, `test_workspace_agent.py`.

---

## Diagram HITL w Workspace

```mermaid
flowchart LR
    subgraph ui [Workspace UI]
        ReviewPanel[#Review]
        Chat[Chat AO]
    end

    subgraph api [FastAPI]
        WR[/workspace/review/*]
        OP[/operator/*]
    end

    subgraph db [(data/dev.db)]
        AR[approval_requests]
        AUD[audit_events]
    end

    ReviewPanel --> WR
    OP --> AR
    WR --> AR
    WR --> AUD
    Chat --> WR
```

---

## Odchylenia od Kanonu

| Kanon | Implementacja |
|-------|---------------|
| Drag status na Board | Select dropdown — prostsze, testowalne |
| iframe Review | Native fetch API — lepsze UX |
| Badge Review | Dodane poza pierwotnym Sprint 2 — `d0f219b` |

---

## Testy

- Integration: review pending, approve flow w `test_workspace_mvp.py`
- Unit: `test_review_queue.py`
- E2E: review panel + attention query (`e2e/tests/workspace.spec.ts`)

---

## Powiązane commity

- `2526053` — board, planning, review routes + UI
- `d0f219b` — review badge + attention summaries
- `3ec1e03` — fix loadReview JS
