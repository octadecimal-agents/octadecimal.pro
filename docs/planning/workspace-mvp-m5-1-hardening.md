<link rel="stylesheet" href="../styles/main.css">

# Faza M5.1 — Domknięcie MVP (hardening)

[← Workspace MVP roadmap](workspace-mvp-roadmap.md) · [Workspace MVP (EN)](../architecture/workspace-mvp.md) · [E2E README](../../e2e/README.md)

**Status:** ✅ ukończone · **2026-06-15**

## Cel fazy

Zamienić działający prototyp Sprint 0–3 w **domknięty, powtarzalny MVP**: formalna akceptacja checklisty Kanonu, ochrona regresji w CI, stabilność codziennego dev (seed, health, brakujące panele hash).

Nie dodajemy nowych możliwości biznesowych — **utwardzamy to, co już jest**.

---

## Kontekst architektoniczny

```text
Developer / CI
    │
    ├── uv run pytest          (110 testów — już w CI)
    │
    └── cd e2e && npm test     (9 scenariuszy Playwright — lokalnie)
            │
            └── webServer → scripts/octa-e2e-server.sh
                    ├── izolowany DATABASE_URL
                    ├── KNOWLEDGE_ROOT = e2e/.data/knowledge
                    └── port 18042
```

Workspace to **cienki adapter** nad istniejącym jądrem:

- UI: `adapters/workspace/static/` (vanilla JS, bez bundlera)
- API: `adapters/workspace/router.py` (`/workspace/*`)
- HITL: ta sama baza co `/operator/` (`data/dev.db` lub `DATABASE_URL`)
- Ledger: `OCTA_LEDGER` (SQLite osobno od approvals)

Hardening dotyczy **granicy dev/prod lokalnego** i **powtarzalności**, nie refaktoru domeny.

---

## Zadania — szczegóły

### M5.1.1 — Checklist akceptacji Kanonu

**Problem:** Sprinty 0–3 zrealizowały funkcje, ale §10 `mvp-localhost-m5.md` nie został formalnie odhaczony.

**Kroki:**

1. Uruchomić `./scripts/octa-mvp-up.sh` na czystym env (bez starych procesów na `:8042`).
2. Przejść każdy punkt checklisty ręcznie + E2E jako dowód automatyczny.
3. Odhaczyć w Kanonie (`Knowledge/.../mvp-localhost-m5.md` §10).
4. Zanotować odchylenia (np. journal path — dziś `OCTA_STATE_DIR` vs `_system/journal/`).

**Done when:** wszystkie punkty PASS; odchylenia opisane w ADR lub workspace-mvp.md.

---

### M5.1.2 — CI Playwright E2E

**Problem:** E2E działa lokalnie, ale nie blokuje regresji na `main`.

**Architektura CI:**

```yaml
# .github/workflows/workspace-e2e.yml (propozycja)
jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - checkout + uv sync
      - cd e2e && npm ci && npx playwright install chromium
      - npm test   # webServer uruchamia octa-e2e-server.sh
```

**Decyzje:**

| Temat | Rozwiązanie |
|-------|-------------|
| Port | `18042` — nie koliduje z dev `:8042` |
| Przeglądarka | `PLAYWRIGHT_BROWSERS_PATH=e2e/.playwright-browsers` (cache w CI) |
| LLM | `LLM_PROVIDER=dry` w skrypcie E2E — zero sekretów w CI |
| RAG | `RAG_BACKEND=memory` + minimalny `Backup.md` w fixture |

**Kroki implementacji:**

1. Nowy workflow obok `python-quality.yml`.
2. `npm ci` wymaga `package-lock.json` w repo (commit lockfile).
3. Timeout jobu ≥ 5 min (seed + uvicorn startup).
4. Artefakt: `playwright-report/` przy failure.

**Done when:** push/PR na `main` uruchamia 9 testów zielonych.

---

### M5.1.3 — Idempotentny `seed_demo.py`

**Problem:** każde `octa-mvp-up.sh` / restart dodaje 3 pending approvals → badge `#Review` rośnie (21+).

**Koncepcja:**

```text
seed_demo.py
    ├── --reset     usuwa demo-* z DB, potem seed
    ├── domyślnie   skip jeśli demo już istnieje (idempotent)
    └── DATABASE_URL z env (już wspierane)
```

**Architektura:** seed to **adapter dev**, nie use case produkcyjny. Może bezpośrednio używać SQLAlchemy — bez przenoszenia do application layer.

**Kroki:**

1. Dodać `argparse`: `--reset`, `--force`.
2. Przed insert: `SELECT COUNT(*) WHERE request_id LIKE 'demo-%'`.
3. `octa-mvp-up.sh`: wywołać `seed_demo.py` bez duplikacji (np. tylko gdy brak demo).
4. Test unit: dwa razy `seed()` → stała liczba rekordów.

**Done when:** 10× restart → badge Review = 3 (lub 0 po `--reset` + seed).

---

### M5.1.4 — Panel `#Zasady`

**Problem:** Kanon przewiduje hash `#Zasady` (linki do OCTA-ZALOZENIA, policy) — brak w UI.

**Rozwiązanie:** statyczny panel **bez RAG** — tylko markdown linki / `<ul>` z URL-ami Kanonu.

**Pliki:**

- `static/index.html` — sekcja `#panel-Zasady`, nav link
- `static/app.js` — `setHash` już generyczny; ewentualnie `loadZasady()` pusta
- `static/styles.css` — reuse `.panel`

**Linki docelowe (przykład):**

- `Knowledge/.../OCTA-ZALOZENIA.md` (file:// lub GitHub raw — decyzja UX)
- `docs/architecture/workspace-mvp.md`
- `CONTRIBUTING.md`

**Done when:** sidebar `#Zasady`, brak błędu konsoli, E2E opcjonalny smoke.

---

### M5.1.5 — Placeholdery poza MVP

**Problem:** `#Dev`, `#Burndown`, `#Ranking` w Kanonie jako „wkrótce” — dziś brak nav → użytkownik nie wie, że to świadomy scope cut.

**Rozwiązanie:**

```html
<section class="panel" id="panel-Dev" data-panel="#Dev">
  <h2>#Dev</h2>
  <p class="muted">Wkrótce — integracja z git/BMAD. Poza zakresem MVP M5.</p>
</section>
```

Nav z klasą `nav-link--disabled` lub normalny link z komunikatem w panelu.

**Done when:** klik nie rzuca JS error; copy jasno mówi „poza MVP”.

---

### M5.1.6 — Dokumentacja uruchomienia (< 15 min)

**Problem:** wiedza rozproszona między workspace-mvp.md, octa-mvp-up.sh, Knowledge.

**Deliverable:** sekcja w `README.md` repo **lub** skrót w Kanonie z jednym flow:

```bash
git clone … && cd octadecimal.pro
uv sync
./scripts/octa-mvp-up.sh
open http://127.0.0.1:8042/
```

**Checklist nowego deva:** Node tylko jeśli E2E; Docker tylko jeśli Qdrant; Keychain opcjonalny dla MiniMax.

**Done when:** osoba trzecia odpala bez pomocy autora.

---

### M5.1.7 — Runbook uprawnień kalendarza

**Problem:** `CALENDAR_PROVIDER=auto` wymaga Calendars permission dla Terminal/Cursor — w sandboxie pada na fixture.

**Rozwiązanie:** runbook w docs (nie kod):

1. System Settings → Privacy & Security → Calendars
2. Włączyć Terminal / Cursor / iTerm
3. `uv run python -c "… list_today_calendar_events …"` smoke
4. Cache: `~/.octa/calendar-cache.json`

**Done when:** na M5 z uprawnieniami `#Planning` pokazuje live event + `source=macos`.

---

### M5.1.8 — Health rozszerzony

**Problem:** `/workspace/health` ma podstawowe pola; debug sync/LLM wymaga logów.

**Propozycja schema (rozszerzenie):**

```json
{
  "documents_indexed": 251,
  "rag_backend": "qdrant",
  "llm_provider": "minimax",
  "llm_available": true,
  "review_pending_count": 3,
  "knowledge_manifest_age_seconds": 3600,
  "knowledge_last_sync_at": "2026-06-14T10:00:00Z",
  "calendar_provider": "auto",
  "calendar_source": "cache"
}
```

**Implementacja:**

- `WorkspaceHealthResponse` w `schemas.py`
- Odczyt `manifest-dev.json` mtime z `KNOWLEDGE_ROOT/.knowledge-index/`
- `ChatCompletionProvider.is_available()` for LLM — `true` when external API key/token is configured; `false` for dry/heuristic mode

**Done when:** `curl /workspace/health | jq` wystarcza do diagnozy bez logów.

---

## Ryzyka

| Ryzyko | Mitigacja |
|--------|-----------|
| CI Playwright flaky | `workers: 1`, retry: 1, izolowany DB |
| Lockfile npm konflikt | `npm ci` tylko w CI |
| Journal path vs Kanon | ADR lub env `OCTA_JOURNAL_DIR` |

---

## Kryterium ukończenia fazy

- [x] Checklist Kanonu §10 — PASS ([sign-off](workspace-mvp-m5-1-signoff.md))
- [x] GitHub Actions: pytest + Playwright
- [x] Seed idempotentny
- [x] `#Zasady` + placeholdery w UI
- [x] README quick start < 15 min
- [x] Health rozszerzony udokumentowany
- [x] Runbook kalendarza macOS

---

## Powiązane commity (propozycja)

1. `ci(e2e): add Playwright workflow for workspace MVP`
2. `fix(seed): make seed_demo idempotent with --reset`
3. `feat(workspace): add #Zasady panel and future hash placeholders`
4. `feat(workspace): extend health endpoint for ops debugging`
5. `docs: workspace quick start for new developers`
