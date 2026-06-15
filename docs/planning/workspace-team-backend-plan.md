<link rel="stylesheet" href="../styles/main.css">

# Plan wdrożenia — backend-team

[← Triple-track](workspace-mvp-triple-track.md) · [M5.6](workspace-mvp-m5-6-m1-server-mode.md) · [Roadmap](workspace-mvp-roadmap.md)

**Zespół:** backend-team · **Framework:** Cursor *(alternatywa: OpenCode + BMAD)* · **Gałęzie:** `feat/m5-*`, `feat/m5-6-*`  
**Kanon PL:** `Knowledge/01-Base-Point/pro/projects/octa-os/plany/zespol-backend-plan.md`

---

## Misja

API, infra, testy i platforma Octa Workspace — od always-on M1 po hosting pc-ubuntu i fazy M6+. **Nie** odpowiada za design system (frontend-team) ani remediację serwerów (security-team), ale **dostarcza kontrakt API/HITL** dla obu.

---

## Faza 0 — MVP core (M5.1–M5.5) ✅

- [x] Sprint 0–3: boot, chat, wiki, board, planning, review, retro
- [x] M5.1 hardening + CI Playwright
- [x] M5.2 RAG scale + policy.yaml T1
- [x] M5.3 AO persona v2 + structured tools + evals
- [x] M5.4 macOS MCP + calctl
- [x] M5.5 daily dev runbook + launchd M5 + Board Octa-native teams
- [x] 169+ pytest, 12 E2E scenarios green

---

## Faza 1 — M5.6 M1 server mode 🔄

**Dokument:** [workspace-mvp-m5-6-m1-server-mode.md](workspace-mvp-m5-6-m1-server-mode.md)  
**Estymata:** 1–2 tygodnie · **Priorytet:** P1

### M5.6.1 launchd na M1

- [x] Plist template + install script (`install-workspace-api-m1-launchd.sh`)
- [x] LaunchDaemon headless (CEO / run_as_ceo)
- [x] Runbook [workspace-m1-server-mode.md](../runbooks/workspace-m1-server-mode.md)
- [ ] 3-dniowy smoke test na fizycznym M1 (reboot + health)
- [x] Smoke dzień 1 auto + cron 09:00 M5→M1 (`octa-m1-smoke-daily.sh`)
- [ ] Weryfikacja kalendarza live `#Planning` na M1

### M5.6.2 Binding sieci

- [x] Domyślnie `127.0.0.1:8042`
- [x] Udokumentować Tailscale LAN (runbook §6 — not enabled MVP)
- [x] Potwierdzić brak public exposure (runbook §6)

### M5.6.3 Kalendarz M1

- [x] `CALENDAR_PROVIDER=auto` w plist
- [ ] EventKit live na M1 — weryfikacja CEO

### M5.6.4 Shortcuts / CLI (opcjonalne)

- [x] `octa workspace open` + `octa workspace smoke` (scripts/octa)
- [x] Dokumentacja w runbooku

### M5.6.5 Failover

- [x] Runbook §7 degradacja gdy M5 dev nadpisuje API
- [ ] Ćwiczenie failover (checklist CEO — [smoke log](../runbooks/workspace-m5-6-smoke-log.md) · [20 min checklist](../runbooks/workspace-m5-6-ceo-checklist.md))

**Sync po M5.6:** powiadomić frontend-team (UX.4) i security-team (SEC.2 agenci M1).

---

## Faza 2 — M5.7 Ubuntu hosting only ⏸

**Dokument:** [workspace-mvp-m5-7-hosting-only.md](workspace-mvp-m5-7-hosting-only.md)  
**Status:** deferred · **Priorytet:** P2

- [ ] M5.7.1 `embed-knowledge sync --prod` → Qdrant pc-ubuntu
- [ ] M5.7.2 HTTPS subdomain + auth
- [ ] M5.7.3 Backup schedule dokumentacja
- [ ] **Bez** floty agentów HYDRA na Ubuntu (ADR 006)

**Sync z security-team:** hosting ≠ agent fleet; security wykonuje z M1 przez SSH.

---

## Faza 3 — M6+ Platform core 🔲

**Dokument:** [workspace-mvp-m6-platform.md](workspace-mvp-m6-platform.md)  
**Status:** parallel · **Priorytet:** P1 (wybrane slice'y)

### Slice priorytetowy (Q2 2026)

- [ ] PostgreSQL persistence (Phase 5)
- [ ] LangGraph HITL production path (Phase 6)
- [ ] OpenTelemetry / Langfuse (Phase 9)
- [ ] Phase 8 guardrails — współpraca z security-team (evals)

### Backlog platformy

- [ ] MCP tool registry rozszerzenie
- [ ] Eval automation w CI
- [ ] Docker Compose dev stack

---

## Faza 4 — Kontrakt dla innych zespołów (ciągły)

### Dla frontend-team

- [x] Review API approve/reject
- [x] Board PATCH tasks
- [x] Health endpoint
- [ ] Stabilizacja API — notatka po M5.6 dla UX.4
- [ ] Nowe pola API tylko na WO frontend-team

### Dla security-team

- [x] HITL Review queue w UI
- [ ] Opcjonalny endpoint webhook/cron trigger raportu (SEC.2)
- [ ] Rozszerzenie `ApprovalRequest` metadata (risk tier, rollback) — WO od security
- [ ] Dokumentacja SYNC-HITL w triple-track

---

## Zasady postępowania

1. **Ownership:** `router.py`, `scripts/` (non-security), launchd, runbooki workspace — tylko backend-team.
2. **PR:** tag `[backend-team]`, CI green, aktualizacja architektury przy zmianie API.
3. **Nie dotykaj** `static/` (poza hotfix) — frontend-team.
4. **Nie dotykaj** `scripts/octa-*-security*`, `security-policy.yaml` — security-team.
5. **Małe PR** — jedna faza / jeden slice na PR.
6. **SSOT:** git + markdown, nie transcript sesji.

---

## Prompt inicjacyjny (copy-paste → Cursor)

```text
Zespół: backend-team
Repo: octadecimal.pro (~/Developer/Repositories/octadecimal-agents/octadecimal.pro)
Framework: Cursor

Przeczytaj obowiązkowo:
- docs/planning/workspace-mvp-triple-track.md
- docs/planning/workspace-team-backend-plan.md (ten dokument)
- docs/planning/workspace-mvp-m5-6-m1-server-mode.md
- docs/architecture/workspace-mvp.md

Twoja misja: infra + API Workspace. Aktualny focus: M5.6 — domknięcie smoke testów M1,
kalendarz live, opcjonalnie M5.6.4 Shortcuts.

NIE dotykaj:
- src/.../workspace/static/ (frontend-team)
- scripts/octa-*-security*, security-policy.yaml (security-team)
- design-artifacts/ (frontend-team)

Po zamknięciu slice'a M5.6:
- zaktualizuj checkboxy w workspace-team-backend-plan.md
- powiadom w docs: API stable for UX.4 i SEC.2 (notatka w triple-track §3.3)

Dashboard CEO (Knowledge) — po każdym slice / bloker / SYNC:
- edytuj WYŁĄCZNIE sekcję TEAM:backend w:
  Knowledge/01-Base-Point/pro/projects/octa-os/triple-track-dashboard.md
- ustaw: postęp % fazy M5.6, następny milestone, bloker, datę aktualizacji
- zaktualizuj pasek M5.6 w sekcji GLOBAL; po zamknięciu M5.6 → SYNC-M16 🟢
- nie edytuj sekcji frontend/security; commit: dashboard(triple-track): [backend-team] …
- szczegóły checkbox → workspace-team-backend-plan.md (SSOT)

Branch: feat/m5-6-<slice>
PR: [backend-team] + zielone pytest i e2e

Weryfikacja:
  uv sync && ./scripts/octa-mvp-up.sh
  uv run pytest
  cd e2e && npm test
```

---

## Prompt inicjacyjny — alternatywa (OpenCode + BMAD)

Użyj, gdy backend-team pracuje w **OpenCode** z metodologią BMAD (story → dev → review → sprint sync). Ten prompt **różni się** od Cursor: wymusza workflow BMAD, story file dla slice'a i jawne sync pointy po fazie.

```bash
cd octadecimal.pro
opencode
```

**Kickoff (copy-paste do OpenCode):**

```text
Zespół: backend-team
Repo: octadecimal.pro
Framework: OpenCode + BMAD Method
Host dev: M5 (build/test) · Host docelowy: M1 (M5.6 server mode)

Przeczytaj obowiązkowo:
- docs/planning/workspace-mvp-triple-track.md (SYNC-API, SYNC-M16, SYNC-HITL)
- docs/planning/workspace-team-backend-plan.md (ten dokument)
- docs/planning/workspace-mvp-m5-6-m1-server-mode.md
- docs/architecture/workspace-mvp.md
- docs/runbooks/workspace-m1-server-mode.md
- ADR 006 (M5-only, no HYDRA on Ubuntu)

Aktualny focus: M5.6 — smoke test M1 (3 dni), kalendarz live EventKit, opcjonalnie M5.6.4 Shortcuts.

Workflow BMAD (kolejność dla slice'a M5.6):
1. /bmad-sprint-status — stan M5.6 vs checkboxy w workspace-team-backend-plan.md
2. /bmad-create-story — story file dla bieżącego slice'a (np. M5.6.1 smoke, M5.6.3 calendar)
   LUB istniejący plan fazy jako kontekst story
3. /bmad-investigate — jeśli obszar nieznany (launchd M1, calendar provider, binding)
4. /bmad-quick-dev LUB /bmad-dev-story — implementacja / domknięcie story (scripts/, router, runbook)
5. /bmad-testarch-atdd — czerwone testy akceptacji jeśli nowy kontrakt API (WO od frontend/security)
6. /bmad-code-review — adversarial review PR przed merge
7. /bmad-checkpoint-preview — checkpoint CEO: health M1, #Planning live, reboot OK
8. Po zamknięciu slice'a M5.6: /bmad-sprint-status update + notatka SYNC-M16 dla frontend (UX.4) i security (SEC.2)

Komendy OpenCode: .opencode/commands/bmad-*.md

NIE dotykaj:
- src/.../workspace/static/ (frontend-team)
- design-artifacts/ (frontend-team)
- scripts/octa-*-security*, security-policy.yaml, security-artifacts/ (security-team)

Ownership backend:
- scripts/ (non-security), launchd, docs/runbooks/workspace-*, router.py, schemas, e2e (przy API)

Sync z innymi zespołami:
- Zmiana API → aktualizuj docs/architecture/workspace-mvp.md + powiadom frontend (SYNC-API)
- Nowe pole Review/HITL → WO od security-team (SYNC-HITL)
- Po M5.6 smoke OK → notatka w triple-track §3.3: „API stable for UX.4 / SEC.2 ready”

Output (wg slice'a):
- story file w _bmad-output/ lub docs/planning/ (jeśli story-driven)
- zaktualizowane checkboxy w workspace-team-backend-plan.md
- runbook delta jeśli operacje M1 się zmieniły
- dashboard CEO: sekcja TEAM:backend w Knowledge/.../triple-track-dashboard.md
  (postęp %, milestone, bloker, SYNC-M16 po M5.6; nie edytuj innych zespołów)

Branch: feat/m5-6-<slice> (np. feat/m5-6-smoke, feat/m5-6-calendar)
PR: [backend-team]
Weryfikacja obowiązkowa:
  uv sync && uv run pytest
  cd e2e && npm test
  (M1) health :8042 po reboot · #Planning calendar source=macos

Metodologia: 1 slice M5.6 = 1 story = 1 PR; ADR 006 — bez HYDRA / sync --prod w tej fazie.
```

**Mapowanie faz backend → BMAD:**

| Faza / slice | Komenda BMAD | Cel |
|--------------|--------------|-----|
| M5.6 planowanie | `/bmad-sprint-status` | który checkbox domknąć |
| Nowy slice | `/bmad-create-story` + `/bmad-dev-story` | story file → implementacja |
| Nieznany kod (launchd, MCP) | `/bmad-investigate` | mental model przed zmianą |
| Implementacja infra/API | `/bmad-quick-dev` | scripts, router, runbook |
| Nowy endpoint (WO) | `/bmad-spec` + `/bmad-testarch-atdd` | kontrakt + testy akceptacji |
| PR przed merge | `/bmad-code-review` | regresja, ownership |
| Weryfikacja CEO | `/bmad-checkpoint-preview` | smoke M1, demo #Planning |
| M6+ platform slice | `/bmad-create-architecture` → `/bmad-dev-story` | większe zmiany platformy |
| Po epoce M5.6 | `/bmad-retrospective` | lessons learned (opcjonalnie) |

---

## Powiązane

- [Triple-track](workspace-mvp-triple-track.md)
- [Daily dev runbook](../runbooks/workspace-daily-dev.md)
- [M1 server runbook](../runbooks/workspace-m1-server-mode.md)
- [ADR 006](../adr/006-m5-only-dev-strategy.md)
- OpenCode BMAD: `.opencode/commands/bmad-dev-story.md`, `bmad-create-story.md`, `bmad-quick-dev.md`, `bmad-code-review.md`, `bmad-sprint-status.md`, `bmad-investigate.md`

---

## Historia

| Data | Zmiana |
|------|--------|
| 2026-06-15 | Utworzenie planu backend-team (triple-track) |
| 2026-06-15 | M5.6.4 CLI + smoke cron + CEO checklist + SYNC-M16 draft |
| 2026-06-15 | Alternatywny prompt OpenCode + BMAD |
