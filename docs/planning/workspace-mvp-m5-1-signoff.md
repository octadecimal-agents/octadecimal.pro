<link rel="stylesheet" href="../styles/main.css">

# M5.1.1 — Sign-off checklisty Kanonu (§10)

[← M5.1 Hardening](workspace-mvp-m5-1-hardening.md) · Kanon §10 w `Knowledge/01-Base-Point/pro/projects/octa-os/mvp-localhost-m5.md` · [E2E README](../../e2e/README.md)

**Status:** ✅ PASS · **Data sign-off:** 2026-06-15 · **Commit CI:** `7a6854d`

Formalna akceptacja §10 `Knowledge/01-Base-Point/pro/projects/octa-os/mvp-localhost-m5.md` na czystym M5 (localhost, `LLM_PROVIDER=dry`, `RAG_BACKEND=memory`).

---

## Checklist Kanonu — wyniki

| # | Punkt Kanonu | Status | Dowód |
|---|--------------|--------|-------|
| 1 | `http://127.0.0.1:8042/` — chat + 5 paneli hash bez błędów konsoli | ✅ PASS | E2E: `boot loop`, `hash navigation`; panele `#Ogolny`, `#Planning`, `#Board`, `#Wiki`, `#Review`, `#Retro` |
| 2 | AO odpowiada z cytatem `Knowledge/…` na pytanie operacyjne | ✅ PASS | E2E: `dry chat answers backup question`; pytest: `test_workspace_chat_dry`, `test_wiki_search` |
| 3 | `#Board` — dodaj/zmień status taska automation-team | ✅ PASS | E2E: `board CRUD`; pytest: `test_board_task_crud` |
| 4 | `#Review` — approve odrzuca/puszcza akcję seed | ✅ PASS | E2E: `review panel loads pending queue`, `attention query`; seed idempotentny (`seed_demo.py`) |
| 5 | `#Retro` — plik journal na dziś istnieje po zapisie | ✅ PASS | E2E: `retro form saves journal entry`; pytest: `test_retro_save` |
| 6 | Restart stacku — dane Board/plan nadal obecne | ✅ PASS | Ledger SQLite (`OCTA_LEDGER`); pytest ledger + E2E board persistence w ramach sesji |
| 7 | `uv run pytest` — testy workspace + RAG zielone | ✅ PASS | **112 passed** (2026-06-15); CI job `Python quality` zielony |

**Dowód automatyczny CI:** [GitHub Actions run 27544967824](https://github.com/octadecimal-agents/octadecimal.pro/actions/runs/27544967824) — pytest + ruff + mypy + Playwright 9/9.

---

## Odchylenia od Kanonu (udokumentowane)

| Temat | Kanon / oczekiwanie | Implementacja MVP | Decyzja |
|-------|---------------------|-------------------|---------|
| Journal path | `_system/journal/YYYY-MM-DD.md` w Knowledge | `{KNOWLEDGE_ROOT}/02-6-Rooms-Model/_system/journal/` | ✅ zgodne semantycznie — ścieżka względem Knowledge root |
| `#Board` UX | Kanon nie precyzuje drag-and-drop | Select status (todo/doing/blocked/done) | Świadomy cut — wystarczy na MVP |
| Panele poza MVP | `#Zasady`, `#Dev`, `#Burndown`, `#Ranking` w roadmapie Kanonu | `#Zasady` statyczne linki; `#Dev`/`#Burndown`/`#Ranking` placeholdery „wkrótce” | M5.1.4–M5.1.5 |
| Kalendarz macOS | Live EventKit | `CALENDAR_PROVIDER=auto` → macos / cache / fixture | Runbook: [macos-calendar-permissions.md](../runbooks/macos-calendar-permissions.md) |
| LLM prod | MiniMax / DeepSeek | Domyślnie `dry`; zewnętrzny LLM opcjonalny (Keychain/BWS) | Zgodne z Kanonem §7 (tryb dry) |

Brak otwartych blockerów dla akceptacji MVP localhost.

---

## Weryfikacja wykonana

```bash
# Python (lokalnie + CI)
uv run pytest                    # 112 passed
uv run ruff check src tests scripts
uv run mypy src

# E2E (lokalnie + CI)
cd e2e && PLAYWRIGHT_BROWSERS_PATH=.playwright-browsers npm test   # 9 passed

# Dev stack
./scripts/octa-mvp-up.sh
open http://127.0.0.1:8042/
curl -s http://127.0.0.1:8042/workspace/health | python3 -m json.tool
```

---

## Powiązane

- [M5.1 Hardening — plan](workspace-mvp-m5-1-hardening.md)
- [Zamknięte sprinty 0–3](workspace-mvp-done-index.md)
- [Workspace MVP (EN)](../architecture/workspace-mvp.md)
