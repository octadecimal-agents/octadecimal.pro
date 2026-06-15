<link rel="stylesheet" href="../styles/main.css">

# Plan wdrożenia — frontend-team

[← Triple-track](workspace-mvp-triple-track.md) · [Roadmap UX backlog](workspace-mvp-roadmap.md#ux-backlog-frontend-team-non-critical)

**Zespół:** frontend-team · **Framework:** OpenCode + WDS + BMAD Method · **Gałęzie:** `feat/ux-*`, `feat/frontend-*`  
**Kanon PL:** `Knowledge/01-Base-Point/pro/projects/octa-os/plany/zespol-frontend-plan.md`

---

## Misja

Wygląd i UX Octa Workspace — design system, responsywność, interakcje paneli hash — **bez blokowania** backend-team (M5.6) ani security-team. Implementacja w `static/` + `design-artifacts/`.

---

## Faza 0 — Stan wyjściowy (MVP funkcjonalny) ✅

- [x] UI hash: `#Ogolny`, `#Planning`, `#Board`, `#Wiki`, `#Review`, `#Retro`, `#Zasady`
- [x] Ciemny motyw CSS variables (`static/styles.css`)
- [x] E2E anchors zdefiniowane ([e2e/tests/workspace.spec.ts](../../e2e/tests/workspace.spec.ts))
- [x] Placeholdery `#Dev`, `#Burndown`, `#Ranking` — świadomie poza scope

**To jest punkt startowy frontend-team** — nie docelowy design `workspace.octadecimal.pro`.

---

## Faza 1 — UX.1 Design system 🔲

**Priorytet:** P0 · **Zależność backend:** brak (tylko `static/`)

### Analiza i spec

- [ ] Audyt obecnego UI vs docelowy `workspace.octadecimal.pro`
- [ ] Tokeny: kolory, typografia, spacing, radius, shadows
- [ ] Spec per panel: `#Ogolny`, `#Board`, `#Review`, `#Planning`, `#Wiki`
- [ ] `design-artifacts/workspace/ux.1-design-system/audit.md`
- [ ] `design-artifacts/workspace/ux.1-design-system/tokens.css` (propozycja)
- [ ] `design-artifacts/workspace/ux.1-design-system/work-order.md`

### Implementacja

- [ ] Branch `feat/ux-design-system`
- [ ] Merge tokenów do `static/styles.css` (PR)
- [ ] Zachowane E2E anchors (SYNC-E2E)
- [ ] Wizualna akceptacja CEO

**Sync:** Work Order review przez backend-team (API wystarczy, E2E plan).

---

## Faza 2 — UX.3 Responsive / mobile 🔲

**Priorytet:** P1 · **Zależność:** UX.1 zalecane

- [ ] Breakpoints (mobile, tablet, desktop)
- [ ] Sidebar collapse / hamburger
- [ ] Touch-friendly Review approve/reject
- [ ] E2E smoke na viewport mobile (opcjonalnie)
- [ ] PR `[frontend-team]` + CI green

---

## Faza 3 — UX.2 Board drag-and-drop 🔲

**Priorytet:** P1 · **Zależność backend:** `PATCH /workspace/board/tasks/{id}` ✅ istnieje

- [ ] WO: `design-artifacts/workspace/ux.2-board-dnd/work-order.md`
- [ ] DnD między kolumnami status
- [ ] Zachowane: `#task-list`, `#new-team`, `#new-title`, `#add-task-btn`, `.badge`
- [ ] E2E update jeśli interakcja wymaga nowych kroków
- [ ] PR + akceptacja CEO

---

## Faza 4 — UX.4 Push / Shortcuts M1 ⏸

**Priorytet:** P2 · **Zależność:** **M5.6 zamknięte** (SYNC-UX4)

- [ ] Czeka na notatkę backend: „API stable for UX.4”
- [ ] Shortcuts: szybki dostęp do `#Review` / `#Planning`
- [ ] Push notification stub (macOS)
- [ ] Dokumentacja w design-artifacts

---

## Faza 5 — UX.5 Voice AO ⏸

**Priorytet:** P2

- [ ] Spec voice UX (design teraz)
- [ ] Implementacja Ollama/Whisper — po UX.1–UX.3
- [ ] Nie blokuje innych zespołów

---

## Faza 6 — UX.6 `#Dev`, `#Burndown`, `#Ranking` ⏸ deferred

**Priorytet:** — · **Wymaga decyzji produktowej CEO**

- [ ] Integracja git / CRM — **nie implementować** bez ADR
- [ ] Placeholder pozostaje

---

## Artefakty docelowe

```text
design-artifacts/workspace/
├── ux.1-design-system/
│   ├── audit.md
│   ├── tokens.css
│   └── work-order.md
├── ux.2-board-dnd/
│   └── work-order.md
├── ux.3-responsive/
│   └── work-order.md
└── design-log.md
```

---

## Zasady postępowania

1. **Ownership:** `static/`, `design-artifacts/` — frontend-team.
2. **Nie dotykaj** bez WO: `router.py`, `scripts/`, launchd, security scripts.
3. **E2E anchors** — nie usuwaj bez aktualizacji testów (SYNC-E2E).
4. **Work Order** przed masowym refaktorem `static/`.
5. **Metodologia:** WDS (`wds-8`, Freya) + BMAD (`bmad-ux`, `quick-dev`, `code-review`, `checkpoint-preview`).
6. **PR:** `[frontend-team]`, rebase na `main` przed merge.

---

## Prompt inicjacyjny (copy-paste → OpenCode + WDS + BMAD)

```bash
cd octadecimal.pro
opencode
```

```text
Zespół: frontend-team
Repo: octadecimal.pro
Framework: OpenCode + WDS + BMAD Method
Agent UX: /wds-agent-freya-ux · Pipeline brownfield: /wds-8-product-evolution

Przeczytaj obowiązkowo:
- docs/planning/workspace-mvp-triple-track.md (SYNC-E2E, SYNC-API, ownership static/)
- docs/planning/workspace-team-frontend-plan.md (ten dokument)
- docs/architecture/workspace-mvp.md
- docs/planning/workspace-mvp-roadmap.md (UX backlog)
- e2e/tests/workspace.spec.ts (anchors do zachowania — nie usuwaj bez update testów)
- _bmad/wds/data/agent-contracts.md (kontrakty agentów WDS)

Tryb: brownfield UX — równoległy do M5.6 (backend-team) i M5.8 (security-team).

Workflow WDS + BMAD (kolejność dla UX.1 — design system):
1. /wds-8-product-evolution — wejście brownfield; scope UX.1 bez refaktoru całego static/
   LUB /wds-agent-freya-ux — discovery + spec z perspektywy UX
2. /bmad-ux — wzorce UX paneli hash (#Ogolny, #Board, #Review, …)
3. /wds-4-ux-design — spec wizualna per panel (layout, stany, tokeny)
4. /wds-7-design-system — tokeny, komponenty; output → design-artifacts/
5. Work Order — work-order.md: pliki do zmiany, anchors E2E, kryteria akceptacji CEO
6. Review WO — backend-team potwierdza: API wystarczy (SYNC-API); brak nowych endpointów dla UX.1
7. /bmad-quick-dev — implementacja w static/ (branch feat/ux-*)
8. /bmad-code-review — PR przed merge (regresja E2E, broken anchors)
9. /bmad-checkpoint-preview — checkpoint wizualny CEO na http://127.0.0.1:8042/

Komendy OpenCode: .opencode/commands/wds-*.md · .opencode/commands/bmad-*.md

NIE dotykaj:
- scripts/, launchd, router.py (chyba że Work Order + backend-team)
- scripts/octa-*-security*, security-policy.yaml, security-artifacts/
- security-team runbooki

Pierwszy cel: UX.1 — design system vs workspace.octadecimal.pro

Output (przed merge do static/):
  design-artifacts/workspace/ux.1-design-system/
    audit.md          — diff obecny UI vs target
    tokens.css        — propozycja tokenów (merge w PR)
    work-order.md     — pliki, anchors, kryteria akceptacji

Handoff implementacji:
- branch feat/ux-design-system
- PR [frontend-team]
- zielone: uv run pytest && cd e2e && npm test
- selektory E2E (#chat-log, #review-list, .btn-approve, .nav-link[data-hash], …) muszą działać

Podgląd lokalny:
  ./scripts/octa-mvp-up.sh && open http://127.0.0.1:8042/

Metodologia: 1 Work Order = 1 PR; nie refaktoruj całego static/ w pierwszej sesji.

Dashboard CEO (Knowledge) — po każdym slice / bloker / SYNC:
- edytuj WYŁĄCZNIE sekcję TEAM:frontend w:
  Knowledge/01-Base-Point/pro/projects/octa-os/triple-track-dashboard.md
- ustaw: postęp % fazy UX.*, następny milestone, bloker, datę aktualizacji
- zaktualizuj pasek UX.1 w sekcji GLOBAL; po SYNC-M16 → odblokuj SYNC-UX4 w opisie
- nie edytuj sekcji backend/security; commit: dashboard(triple-track): [frontend-team] …
- szczegóły checkbox → workspace-team-frontend-plan.md (SSOT)
```

**Mapowanie faz UX → WDS / BMAD:**

| Faza | Komenda | Cel |
|------|---------|-----|
| UX.1 design system | `/wds-8` lub `/wds-agent-freya-ux` → `/wds-7-design-system` | tokeny, audit |
| UX.1 spec paneli | `/bmad-ux` + `/wds-4-ux-design` | layout hash panels |
| UX.1 implementacja | `/bmad-quick-dev` | zmiany `static/` |
| UX.2 Board DnD | `/wds-4-ux-design` → WO → `/bmad-quick-dev` | DnD + E2E update |
| UX.3 responsive | `/wds-4-ux-design` → `/bmad-quick-dev` | breakpoints |
| PR / CEO review | `/bmad-code-review` + `/bmad-checkpoint-preview` | CI + wizualna akceptacja |
| UX.4 Push M1 | czeka SYNC-M16; potem `/bmad-quick-dev` | Shortcuts — po M5.6 |

---

## Powiązane

- [Triple-track](workspace-mvp-triple-track.md)
- [Dual-track legacy](workspace-mvp-dual-track.md) → redirect
- OpenCode WDS: `.opencode/commands/wds-agent-freya-ux.md`, `wds-8-product-evolution.md`, `wds-4-ux-design.md`, `wds-7-design-system.md`
- OpenCode BMAD: `.opencode/commands/bmad-ux.md`, `bmad-quick-dev.md`, `bmad-code-review.md`, `bmad-checkpoint-preview.md`
- WDS: `_bmad/wds/data/agent-contracts.md`

---

## Historia

| Data | Zmiana |
|------|--------|
| 2026-06-15 | Utworzenie planu frontend-team (triple-track) |
| 2026-06-15 | Prompt rozszerzony o workflow WDS + BMAD |
