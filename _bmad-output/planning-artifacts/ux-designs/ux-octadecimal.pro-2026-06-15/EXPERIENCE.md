---
status: draft
updated: 2026-06-15
---

# EXPERIENCE.md — Octa Workspace

## Foundation

- **Form-factor:** Web (desktop-first). docelowo: macOS Catalyst lub PWA.
- **UI system:** Vanilla CSS. DESIGN.md (`{design.colors}`, `{design.typography}`, `{design.components}`) jest wizualną referencją. EXPERIENCE.md opisuje wyłącznie behavioralny delta.
- **Target runtime:** FastAPI + Jinja2/static. Hash-routing w vanilla JS.
- **Protagonista:** Piotr (CEO, jedyny człowiek w firmie). Agenci AI to reszta zespołu.

## Information Architecture

### Model nawigacji: hash routing

Aplikacja działa w modelu SPA-light przez `window.location.hash`. Każdy hash odpowiada panelowi. Jeden panel aktywny naraz. Chat jest zawsze widoczny w dolnej połowie ekranu.

### Spis paneli

| Hash | Panel | Źródło danych | Priorytet UX.1 |
|------|-------|---------------|-----------------|
| `#Ogolny` | Chat główny z AO | `POST /workspace/chat` | P0 |
| `#Planning` | Plan dnia + sprint wewnętrzny | `GET /workspace/planning/*` | P0 |
| `#Board` | Tablica zadań zespołów dev | `GET/POST/PATCH /workspace/board/tasks` | P0 |
| `#Wiki` | Wyszukiwarka bazy wiedzy (RAG) | `GET /workspace/wiki/search` | P0 |
| `#Review` | Kolejka HITL (akceptacje CEO) | `GET /workspace/review/pending`, `POST .../approve\|reject` | P0 |
| `#Retro` | Dziennik + lessons learned | `GET/POST /workspace/retro/*` | P0 |
| `#Zasady` | Kanon, polityki, linki | Statyczne | P0 |
| `#Dev` | Status dev / Cursor (wkrótce) | — | P3 (deferred) |
| `#Burndown` | Velocity sprintu (wkrótce) | — | P3 (deferred) |
| `#Ranking` | Ranking agentów (wkrótce) | — | P3 (deferred) |

### Relacje między panelami

```
#Ogolny (chat) ──sugeruje──→ #Review (gdy są pending)
#Ogolny (chat) ──sugeruje──→ #Wiki (gdy pyta o wiedzę)
#Ogolny (chat) ──sugeruje──→ #Planning (gdy pyta o plan)
#Planning ───generuje───→ #Board (taski z planu → zadania)
#Board ───status───→ #Review (akcje infra wymagają HITL)
#Retro ───push───→ #Wiki (lessons learned → baza wiedzy)
```

### Agent sidebar vs hash tabs

Dwa tryby nawigacji (oba widoczne jednocześnie):
- **Agent sidebar** (lewa kolumna, `w-64`) — lista agentów z awatarami i status dots. Kliknięcie → panel z konwersacją z danym agentem w chacie.
- **Hash tab bar** (górny pasek) — pills z hash panelami. Kliknięcie → przełączenie widoku w content area.

W UX.1 focus jest na hash tab bar. Agent sidebar jest wizualnie wzorowany na targetcie ale behavior będzie rozwijany w UX.4+.

## Voice and Tone

- **Agent Osobisty (AO):** L0 — ciepły, rzeczowy, proaktywny. Mówi per "ty". Zwięzłe podsumowania. Zawsze kończy opcją działania ("Mam zaplanować?", "Otworzyć #Review?").
- **Maja:** L0 — rzeczowa, konkretna, delikatnie formalna. Operacyjna.
- **Paweł:** L0 — suchy, precyzyjny, audit trail tone. W HITL podaje rekomendację.
- **Katarzyna:** L0 — spokojna, precyzyjna, cytuje źródła.
- **Pozostali agenci:** L1+ — zdefiniowani w DESIGN.md Brand & Style.

AO jest domyślnym głosem w `#Ogolny`. Gdy chat dotyczy konkretnego agenta, AO może go "przywołać".

### Konwencje mikroskopijne

- Hash tagi: format `#Panel` — pisane wielką literą, bez spacji
- Przyciski: imperatywy ("Generuj plan", "Wyślij", "Zapisz")
- Empty states: informative, nie "brak danych" tylko "Brak wydarzeń — wygeneruj plan lub zapytaj AO"
- Potwierdzenia: "Zapisano", "Zaakceptowano", "Odrzucono" — nie "Sukces!"

## Component Patterns

### Chat (`.chat-section`)
- Zawsze widoczny w dolnej części ekranu
- Dzielony na: header (`#Ogolny` label) → log → form
- Wiadomości AO przychodzą z różnymi awatarami agentów (nie tylko AO)
- Gdy agent nie jest AO, wiadomość ma jego awatar + name + timestamp
- AO może sugerować hash: "Otwórz #Review" → klikalny link
- Pierwsza wiadomość po starcie: powitanie + health status workspace
- Automatyczne scrollowanie do dołu przy nowej wiadomości

### Board (`.task-grid`)
- Lista `.task-card` z: title, team badge, status select, intent
- Team badge: kolor wg team (design tokens — tagi agentów)
- Status: todo → doing → blocked → done
- `select[data-id]` zmienia status przez PATCH — bez reloadu
- Add task: team select + input + button

### Review (`.review-list`)
- Kolejka pending: description, actor, risk level, action type
- Dwa przyciski: Approve (zielony) + Reject (czerwony)
- Po akcji: usuwa element z listy, aktualizuje badge
- Badge na `#Review` w tab bar: licznik pending, czerwony
- Badge odświeżany po każdej akcji i na starcie

### Planning (`.calendar` + `.plan-list`)
- Kalendarz: lista wydarzeń z time + title + calendar source
- Plan: editable lista z source tag i inputem inline
- Action buttons: "Generuj plan (AO)", "Zapisz edycję"
- Add item: formularz na dole

### Wiki
- Search input + submit → lista wyników
- Wynik: source (filename) + score + excerpt
- Pusty: "Brak wyników."
- Search on submit (nie live)

### Retro
- Form: 3 pola (went_well, improve, tomorrow) + submit
- Preview: istniejący wpis dnia jako `<pre>`
- Po submit: reload preview

## State Patterns

| Stan | Zachowanie | Przykład |
|------|-----------|----------|
| **Loading** | Brak obecnie — ANote: dodać skeleton/spinner w UX.1 | fetch danych panelu — pokaż `.skeleton` lub `Ładowanie...` |
| **Empty** | Komunikat informacyjny, często z CTA | "Brak pozycji — wygeneruj plan lub zapytaj AO." |
| **Error** | API error → wiadomość w chacie | "Błąd: {message}" w .msg.agent |
| **Partial** | Degraded health → warning w powitaniu | "Workspace: Knowledge niedostępne — ustaw KNOWLEDGE_ROOT" |
| **Disabled** | Przycisk disabled podczas ładowania / brak inputu | `disabled:opacity-50 disabled:cursor-not-allowed` |
| **Optimistic** | Brak — dane zawsze z API, nie z cache | fetch po każdej akcji |

### Loading — propozycja na UX.1

Dla każdego panelu z fetch: pokaż `.skeleton` placeholder podczas ładowania danych. Wzór:

```html
<div class="skeleton"><div class="skeleton-line w-3/4"></div><div class="skeleton-line w-1/2"></div></div>
```

Kolory skeleton: `--color-bg-alt` z pulsem przezroczystości.

## Interaction Primitives

### Hash navigation
- Kliknięcie `.nav-link` → `setHash(hash)` → aktualizacja `location.hash`, `.active` class, load danych panelu
- `window.addEventListener("hashchange")` → to samo (back/forward browser)
- Domyślny hash: `#Ogolny`
- Smooth transition między panelami (opcjonalnie: fade)

### Chat submit
- `#chat-form submit` → `sendChat(text)` → POST /workspace/chat → append response
- Enter wysyła, Shift+Enter nowa linia (jeśli textarea)
- Input cleared po submit
- Disabled button gdy input empty

### Review actions
- Approve: POST → remove z listy → animate out → update badge
- Reject: analogicznie
- Potwierdzenie: brak (action jest destruktywne — Reject ma czerwony kolor jako sygnał)

### Status change (Board)
- `select change` → PATCH /workspace/board/tasks/{id} → brak reloadu listy
- Optymistycznie: zmiana od razu w UI, rollback na błędzie

## Accessibility Floor

- `lang="pl"` na `<html>` — obecne, zachować
- `aria-label` na nawigacji sidebar — obecne, rozszerzyć na tab bar
- **Focus management:** przy zmianie hash, focus przeniesiony na nagłówek panelu (`h2`)
- **`aria-live="polite"`** na `#chat-log` — nowe wiadomości czytane przez screen reader
- **`role="tablist"` / `role="tab"`** dla hash tab bar (obecnie `.nav-link` z `data-hash`)
- **`role="region"`** dla każdego panelu z `aria-labelledby`
- **Keyboard navigation:** Tab między elementami, Enter/Spacja aktywuje przyciski
- **Skip to content:** link na początku (`#main-content`)
- **Focus visible:** `:focus-visible` outline (obecnie focus ring przez DESIGN.md)
- **Status messages:** użyć `role="status"` dla powiadomień (approve/reject confirm)
- **Badge count:** `aria-label="Oczekujące akceptacje: {n}"` — obecne, rozszerzyć o liczbę

### Color contrast (light mode — target)

| Pair | Ratio | Pass AA? |
|------|-------|----------|
| `#202124` on `#ffffff` | ~15.5:1 | ✅ |
| `#5f6368` on `#ffffff` | ~6.5:1 | ✅ |
| `#5f6368` on `#f8f9fa` | ~5.8:1 | ✅ |
| `#1a73e8` on `#ffffff` | ~6.1:1 | ✅ |

### Color contrast (dark mode — propozycja)

| Pair | Ratio | Pass AA? |
|------|-------|----------|
| `#e2e8f0` on `#0f111a` | ~13.8:1 | ✅ |
| `#8892a4` on `#0f111a` | ~6.2:1 | ✅ |
| `#4a8cff` on `#0f111a` | ~6.8:1 | ✅ |

## Responsive & Platform

### Breakpoints

| Zakres | Layout |
|--------|--------|
| > 1024px (lg) | Sidebar agentów + tab bar + content + chat — pełny layout |
| 768–1024px (md) | Sidebar chowany (hamburger), tab bar scrollable, content full-width |
| < 768px (sm) | Hash tab bar w wrapping, sidebar slide-in, chat na full width |

### Sidebar na mobile
- Poniżej `lg`: sidebar agentów jako overlay slide-in (z lewej)
- Przycisk hamburger w headerze
- `aria-expanded` na hamburgerze
- Overlay (półprzezroczyste tło) klikalne → zamyka sidebar

### Hash tab bar na mobile
- `overflow-x-auto` z `scrollbar-none` — poziomy scroll
- Aktywny tab w widoku (scrollIntoView przy aktywacji)
- Touch-friendly: min 44px height dla pills

### Input form na mobile
- `py-4` zamiast sm:`py-4` — większy touch target
- Button disabled dopóki input nie jest pusty (zapobiega pustym submit)
- Keyboard: Enter = submit, bez need for button tap

## Key Flows

### Flow 1: Poranny briefing (07:00)

**Protagonista:** Piotr, CEO. Właśnie włączył M1, pierwsza kawa.

1. Piotr otwiera `workspace.octadecimal.pro:8042` → widzi `#Ogolny` (Agent Osobisty)
2. AO wita: *"Dzień dobry! 3 spotkania, 12 maili, 2 przypomnienia. Indeks Knowledge: 80 dokumentów."*
3. Piotr pisze: *"Co ważne?"*
4. AO odpowiada skrótem z kalendarza + wyróżnia 2 priorytety: *"Embed audit o 10:00, ale najpierw triage poczty — mam 2 maile do odpowiedzi."*
5. AO sugeruje: *"Otworzyć #Planning?"*
6. **Climax:** Piotr klika sugerowany hash lub pyta dalej — dzień ma kierunek.

### Flow 2: Sprint Planning (09:00)

**Protagonista:** Piotr, Maja (Chief of Staff) wspiera.

1. Piotr przechodzi do `#Planning` → widzi kalendarz + plan listę
2. Kliknięcie "Generuj plan (AO)" → POST /workspace/planning/generate
3. Plan tygodnia pojawia się jako editable list + taski na `#Board` dla 4 zespołów
4. Piotr edytuje inline pozycje planu
5. Kliknięcie "Zapisz edycję" → PUT /workspace/planning/items
6. **Climax:** Plan gotowy. Piotr przechodzi do `#Board` by zobaczyć taski rozbite na zespoły.

### Flow 3: HITL Review (13:30)

**Protagonista:** Piotr, Paweł (Security) pre-audytuje.

1. AO przypomina: *"W kolejce #Review czekają 3 akcje — merge PR, deploy strony, zmiana policy tier."*
2. Piotr przechodzi do `#Review` → lista pending
3. Każda pozycja ma: description, actor, risk level, action type. Security podpisał rekomendację.
4. Piotr approve na 2, reject na 1 (z rozumieniem ryzyka)
5. Badge na `#Review` aktualizuje się po każdej akcji
6. **Climax:** Wszystkie akcje rozpatrzone. AO potwierdza w chacie: *"2/3 zaakceptowane. Deploy idzie dalej."*

### Flow 4: Day Closeout / Retro (17:00)

**Protagonista:** Piotr, Katarzyna (Knowledge) finalizuje.

1. Piotr przechodzi do `#Retro`
2. Widzi form → wypełnia 3 pola: co poszło dobrze, co poprawić, jutro
3. Submit → POST /workspace/retro → preview aktualizuje się
4. Kliknięcie "Zapisz" → PUT /workspace/retro (jeśli edycja)
5. Lessons learned → automatyczny push do bazy wiedzy (Katarzyna)
6. **Climax:** Dzień zamknięty. AO: *"Zapisano. Jutro zaczniemy od #Review — czeka 1 nowa akcja z automatu."*

### Flow 5: Deep Work — Dev mode (10:00–12:30)

**Protagonista:** Piotr, Wilson (automation) wspiera.

1. Piotr pracuje w Cursorze z BMAD (Amelia). Workspace otwarte w tle.
2. AO w trybie watchdog: monitoruje embed, alertuje tylko przy problemach.
3. automation-team (Wilson) async pracuje na `#Board` — taski robione, status zmieniany przez API
4. Piotr sprawdza `#Board` co 30-60 min: widzi postęp, zmiany status
5. Jeśli task zablokowany → AO sugeruje: *"Wilson czeka na decyzję — sprawdź #Review."*
6. **Climax:** Bloker rozwiązany przez HITL. Praca płynie dalej.
