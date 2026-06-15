# Audyt UI — Octa Workspace MVP
**Data:** 2026-06-15 · **Wersja:** obecna (`static/`)

## Struktura

| Plik | Lokalizacja |
|------|-------------|
| `index.html` | `src/.../workspace/static/index.html` (143 linie) |
| `styles.css` | `src/.../workspace/static/styles.css` (420 linii) |
| `app.js` | `src/.../workspace/static/app.js` (317 linii) |

## Stan obecny — podsumowanie

### Layout
- Grid 2-kolumnowy: sidebar 220px + main (dół podzielony na panel + chat)
- Brak sticky header / footer
- Breakpoint 800px — sidebar collapse do poziomego wrappingu (surowe)
- Brak płynnego sidebar collapse / hamburgera

### Sidebar (nawigacja hash)
- 7 aktywnych paneli: `#Ogolny` · `#Planning` · `#Board` · `#Wiki` · `#Review` · `#Retro` · `#Zasady`
- 3 placeholder-y (wkrótce): `#Dev` · `#Burndown` · `#Ranking`
- Badge `#Review` zlicza pending — działa, ale ukryty gdy 0
- Brak wizualnego feedbacku aktywności poza kolorem tła

### Kolory / Motyw
- Tylko **dark mode** (zmienne CSS w `:root`)
- 7 zmiennych kolorów: bg, surface, border, text, muted, accent, accent-soft, success, danger
- Brak zmiennych dla: hover states, sekundarny accent, gradienty
- Indigo (`#6366f1`) jako jedyny accent — wszystko niebiesko-fioletowe

### Typografia
- `Segoe UI`, system-ui, sans-serif
- Jeden rozmiar skalujący
- Brak: heading scale, font-weight scale, mono (code)

### Komponenty
- **Chat:** `.msg.user` / `.msg.agent` — proste bąbelki, max-width 85%
- **Board:** `.task-card` — karty z select status, badge team
- **Wiki:** lista wyników (`.wiki-results li`)
- **Review:** lista + `.btn-approve` / `.btn-reject`
- **Retro:** formularz inline
- **Planning:** calendar items + editable list
- **Zasady:** statyczna lista linków

### Stan komponentów
| Stan | Obsłużony? |
|------|-----------|
| Pusty | TAK (np. "Brak wyników", "Kolejka pusta") |
| Ładowanie | NIE — żadnego spinnera / skeleton |
| Błąd API | TAK (catch → appendMessage) |
| Edge: offline | NIE |

### Responsywność
- Media query przy 800px — jedna linia
- Mobile: sidebar flex-wrap, layout grid → 1fr
- Brak: hamburger, sidebar slide, touch-friendly spacing

### Accessibility
- `lang="pl"` — OK
- `aria-label` na nav i badge — OK
- Brak: `aria-live` na chat-log, focus management przy hash change, skip-to-content, keyboard navigation dla paneli

### JavaScript
- Vanilla JS, brak frameworka
- Fetch-based API calls
- Hash routing w `onhashchange`
- Brak: WebSocket, optimistic UI, cache, offline SW

## Co działa dobrze
- Ciemny motyw z CSS variables — łatwo tokenizować
- Architektura hash paneli prosta i przewidywalna
- E2E anchors konsekwentnie użyte
- API error handling w chat (try/catch → message)

## Główne luki vs planowany design system
1. **Brak tokenów** — kolory, spacing, radius, shadows inline lub w :root (tylko 7 var)
2. **Brak design reference** — nie wiadomo do czego dążymy
3. **Brak component library** — każdy panel ma własne wzorce
4. **Jeden motyw** — tylko dark, brak light mode
5. **Brak systemowej typografii** — scale, weights, line-height
6. **Stanów loading brak** — wszystko na fetch, użytkownik nie widzi progresu
7. **Responsywność minimalna** — sidebar nie jest "prawdziwym" collapse
