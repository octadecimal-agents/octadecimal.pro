---
title: 'UX.1 — Design system tokens'
type: 'feature'
created: '2026-06-15'
baseline_commit: 'e32c4967324afa8861a5dee16de916732d9d483c'
status: 'done'
context:
  - '_bmad-output/planning-artifacts/ux-designs/ux-octadecimal.pro-2026-06-15/DESIGN.md'
  - '_bmad-output/planning-artifacts/ux-designs/ux-octadecimal.pro-2026-06-15/EXPERIENCE.md'
  - '_bmad-output/planning-artifacts/ux-designs/ux-octadecimal.pro-2026-06-15/audit.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Obecne UI workspace (`static/`) ma tylko 7 CSS variables, brak systemu tokenów, brak light mode, indigo accent #6366f1 zamiast docelowego #1a73e8. Layout hash paneli jest surowy — brak agent sidebaru i tab pill UI.

**Approach:** Adoptować tokeny z workspace.octadecimal.pro (kolory, Inter font, radius hierarchy, spacing scale) z dark/light dualnym motywem. Zaktualizować index.html o strukturę sidebar + tab bar + chat feed zgodną z targetem.

## Boundaries & Constraints

**Always:**
- Zachować wszystkie E2E anchors (`#chat-log`, `#review-list`, `.btn-approve`, `.btn-reject`, `.nav-link[data-hash]`, `#task-list`, `#new-team`, `#new-title`, `#add-task-btn`, `.badge`, `#wiki-query`, `#wiki-form`, `#wiki-results`, `#chat-input`, `#chat-form`, `#panel-*`, `#calendar-list`, `#generate-plan-btn`, `#plan-list`, `#retro-form`, `#retro-preview`, `#review-badge`)
- Zachować wszystkie funkcje JS (chat, board CRUD, planning, wiki search, review, retro, hash routing)
- CSS variables w `:root` z `[data-theme="light"]` i `[data-theme="dark"]` selektorami
- Inter font przez Google Fonts (link w `<head>`)
- Accent #1a73e8 (light) / #4a8cff (dark)

**Ask First:**
- Zmiana struktury HTML sidebaru (nav → aside z agent items)
- Dodanie theme toggle UI

**Never:**
- Nie zmieniać logiki JS (tylko CSS + HTML struktura)
- Nie zmieniać router.py, scripts/, API endpoints
- Nie dodawać frameworków (React, Vue, Tailwind) — vanilla CSS

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Theme toggle | Kliknięcie przycisku theme | HTML `data-theme` switch light↔dark | Persist choice w localStorage |
| Stary hash link | Użytkownik z bookmarks `#Ogolny` | Panel ładuje się normalnie (id zmienione z #Ogolny → #Ogólny jeśli zmieniamy) | Zachować `#Ogolny` jako alias |

</frozen-after-approval>

## Code Map

- `src/secure_agentic_ai/adapters/workspace/static/styles.css` — główny CSS: zastąpić :root tokenami, dodać `[data-theme]`, nowe komponenty (sidebar, tab pill, message, input)
- `src/secure_agentic_ai/adapters/workspace/static/index.html` — HTML: agent sidebar, tab pill bar, nowa struktura chat feed, theme toggle
- `src/secure_agentic_ai/adapters/workspace/static/app.js` — JS: theme toggle obsługa + localStorage

## Tasks & Acceptance

**Execution:**
- [x] `styles.css` -- Zastąpić `:root` zmienne nowym systemem tokenów (dark/light przez `[data-theme]`), dodać komponenty: `.sidebar`, `.agent-item`, `.status-dot`, `.tab-bar`, `.tab-pill`, `.message`, `.input-area`. Zachować wszystkie istniejące klasy dla paneli (`.panel`, `.task-card`, `.badge`, `.review-list`, itp.)
- [x] `index.html` -- Zrestrukturyzować layout: sidebar z agentami (lewa kolumna), tab pill bar (górny pasek), chat feed (środkowa sekcja), input form (dół). Zachować wszystkie istniejące `id` dla E2E anchors.
- [x] `app.js` -- Dodać funkcję `toggleTheme()` + localStorage persist. Reszta JS bez zmian.

**Acceptance Criteria:**
- Given otwarty workspace na `:8042`, when strona się ładuje, then widoczny jest sidebar z 9 agentami + tab bar z hash panelami + chat feed
- Given strona w light mode, when kliknięty theme toggle, then przełącza na dark mode i odwrotnie
- Given odświeżenie strony w dark mode, when localStorage pamięta preferencję, then dark mode pozostaje
- Given istniejące E2E testy, when `cd e2e && npm test`, then wszystkie przechodzą

## Design Notes

Tokeny w DESIGN.md (`_bmad-output/.../DESIGN.md`) — source of truth dla kolorów, fontów, radiusów, spacingu.

Kluczowe klasy do zachowania (E2E anchors): `#chat-log`, `#chat-input`, `#chat-form`, `#review-list`, `.btn-approve`, `.btn-reject`, `.nav-link[data-hash]`, `#task-list`, `#new-team`, `#new-title`, `#add-task-btn`, `.badge`, `#wiki-query`, `#wiki-form`, `#wiki-results`, `#panel-*`, `#calendar-list`, `#generate-plan-btn`, `#plan-list`, `#retro-form`, `#retro-preview`, `#review-badge`.

Po zmianach: `panel-Ogolny` zamiast `panel-Ogólny` — zachować spójność. Obecnie HTML ma `id="panel-Ogolny"` (bez akcentu).

## Verification

**Commands:**
- `cd e2e && npm test` -- expected: wszystkie 12 testów green
- `uv run pytest tests/integration/test_workspace_mvp.py` -- expected: API tests green

## Suggested Review Order

**Design tokens (entry point)** — nowy system dark/light dual, #1a73e8 accent, Inter font

  [`styles.css:1`](../../src/secure_agentic_ai/adapters/workspace/static/styles.css#L1)

**Sidebar agentów** — 9 agentów z avatarami + status dots, sidebar-header

  [`styles.css:71`](../../src/secure_agentic_ai/adapters/workspace/static/styles.css#L71)

**Tab pill navigation** — .nav-link z .tab-pill dla zachowania E2E anchors

  [`styles.css:147`](../../src/secure_agentic_ai/adapters/workspace/static/styles.css#L147)

**HTML restrukturyzacja** — sidebar aside + tab bar nav + content-area + theme toggle

  [`index.html:1`](../../src/secure_agentic_ai/adapters/workspace/static/index.html#L1)

**Theme toggle JS** — initTheme z localStorage persist

  [`app.js:317`](../../src/secure_agentic_ai/adapters/workspace/static/app.js#L317)
