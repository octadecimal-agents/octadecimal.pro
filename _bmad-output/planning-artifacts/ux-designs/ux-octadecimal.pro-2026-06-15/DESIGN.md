---
colors:
  accent: "#1a73e8"
  accent-hover: "#1765CC"
  destructive: "#ea4335"
  success: "#34a853"
typography:
  sans: "Inter, system-ui, -apple-system, sans-serif"
  mono: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas"
rounded:
  full: 9999
  xl: 12
  lg: 8
  md: 6
spacing:
  base: 4
components:
  sidebar-agent-item: true
  hash-tab: true
  chat-message: true
  input-form: true
status: draft
updated: 2026-06-15
---

# DESIGN.md — Octa Workspace

> Na podstawie targetu `workspace.octadecimal.pro` (workspace app UI).

## Brand & Style

Octa Workspace to profesjonalne środowisko pracy zespołu AI. Styl: **czysty, Google-scale, materiałowy** — dużo whitespace, subtelne cienie, zaokrąglone rogi. Komunikacja na pierwszym planie (chat feed), narzędzia w tle (hash panele). Brand voice w EXPERIENCE.md.

**Motyw:** dualny dark/light przez CSS variables. `[data-theme="dark"]` / `[data-theme="light"]` na `<html>`. Domyślny: dark (zgodność z istniejącym MVP).

## Colors

### Light mode (target)

| Token | Wartość | Użycie |
|-------|---------|--------|
| `--color-accent` | `#1a73e8` | linki, przyciski primary, active tab, focus ring |
| `--color-accent-hover` | `#1765CC` | hover na buttonach primary |
| `--color-accent-soft` | `#E8F0FE` | tło aktywnego taba, highlight |
| `--color-bg` | `#ffffff` | tło główne |
| `--color-bg-alt` | `#f8f9fa` | tło sekundarne (hover, card alt) |
| `--color-bg-alt2` | `#f1f3f4` | tło tertiary |
| `--color-text-primary` | `#202124` | tytuły, body |
| `--color-text-secondary` | `#5f6368` | metadane, opisy, timestampy |
| `--color-border` | `#DADCE0` | główne border (containery, inputy) |
| `--color-border-light` | `#E8EAED` | subtelne border (dividers, sidebar) |
| `--color-destructive` | `#ea4335` | błędy, delete, reject |
| `--color-success` | `#34a853` | approve, working status |
| `--color-status-planning` | `#9aa0a6` | planning/pending badge |

### Sidebar (dark)

| Token | Wartość | Użycie |
|-------|---------|--------|
| `--color-bg-sidebar` | `#1e1e2e` | tło sidebaru (agent list) |
| `--color-bg-sidebar-hover` | `#2a2a3e` | hover na agencie |
| `--color-bg-sidebar-active` | `#3a3a5e` | selected agent |
| `--color-text-sidebar` | `#cdd6f4` | text w sidebarze |
| `--color-text-sidebar-dim` | `#6c7086` | secondary text w sidebarze |

### Status dots (agent presence)

| Token | Wartość | Znaczenie |
|-------|---------|-----------|
| `--color-status-working` | `#34a853` | aktywny, pracuje (zielona kropka) |
| `--color-status-review` | `#1a73e8` | wymaga review / oczekuje (niebieska kropka) |
| `--color-status-planning` | `#9aa0a6` | planowanie / pending (szara kropka) |

### Tagi agentów (role)

| Rola | Tło | Text |
|------|-----|------|
| Working (domyślny) | `#E6F4EA` | green tint |
| Knowledge | `#F3E8FD` | purple tint `#8430CE` |
| Ops/DevOps | `#FEF7E0` | amber tint `#E8A000` |
| Product/PO | `#E8F0FE` | blue tint (accent) |

### Dark mode — propozycja

| Token | Wartość | Odpowiednik light |
|-------|---------|-------------------|
| `--color-bg` | `#0f111a` | `#ffffff` |
| `--color-bg-alt` | `#1a1d2e` | `#f8f9fa` |
| `--color-bg-sidebar` | `#0a0c13` | `#ffffff` |
| `--color-bg-sidebar-hover` | `#1a1d2e` | `#f8f9fa` |
| `--color-bg-sidebar-active` | `#252840` | `#E8F0FE` |
| `--color-text-primary` | `#e2e8f0` | `#202124` |
| `--color-text-secondary` | `#8892a4` | `#5f6368` |
| `--color-border` | `#1e293b` | `#DADCE0` |
| `--color-border-light` | `#1a1f2e` | `#E8EAED` |
| `--color-accent` | `#4a8cff` | `#1a73e8` |
| `--color-accent-hover` | `#6ba3ff` | `#1765CC` |
| `--color-accent-soft` | `rgba(74, 140, 255, 0.15)` | `#E8F0FE` |

## Typography

| Token | Wartość |
|-------|---------|
| Font sans | `Inter, system-ui, -apple-system, sans-serif` |
| Font mono | `ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas` |
| Body size | `14px` (0.875rem) · line-height `1.5` |
| Body text | `--color-text-primary` |

### Scale

| Poziom | rem | px | Użycie |
|--------|-----|----|--------|
| `xs` | 0.75 | 12 | tagi, notki, nav-soon |
| `sm` | 0.875 | 14 | body, input text, agent role |
| `base` | 1 | 16 | nagłówki paneli (h2) |
| `lg` | 1.125 | 18 | hero / sekcje |
| `xl` | 1.25 | 20 | |
| `2xl` | 1.5 | 24 | headingi sekcji |

### Weights

| Waga | Użycie |
|------|--------|
| 400 (normal) | body, opisy |
| 500 (medium) | agent name, button text |
| 600 (semibold) | nagłówki, linki |
| 700 (bold) | brand, tytuły |

## Layout & Spacing

### Base unit: `4px` (`0.25rem`) — Tailwind spacing scale

| Token | rem | px | Użycie |
|-------|-----|----|--------|
| `spacing-1` | 0.25 | 4 | gap minimalny |
| `spacing-2` | 0.5 | 8 | padding icon, gap między elementami |
| `spacing-3` | 0.75 | 12 | gap w listach, padding inputów |
| `spacing-4` | 1 | 16 | padding paneli, sidebar |
| `spacing-5` | 1.25 | 20 | |
| `spacing-6` | 1.5 | 24 | padding sekcji, container padding |

### Workspace layout (target)

```
┌──────────────────────────────────────────────────────────┐
│  Container (rounded-xl, border, shadow-sm, bg-white)      │
│  ┌──────────┬───────────────────────────────────────────┐ │
│  │ Sidebar  │  Tab bar (overflow-x, scrollbar-none)      │ │
│  │ (w-64)   ├───────────────────────────────────────────┤ │
│  │ Agent    │  Content area (overflow-y)                 │ │
│  │ list     │  ┌───────────────────────────────────────┐ │ │
│  │          │  │ Chat feed (messages)                   │ │ │
│  │          │  │ ┌───┬──────────────────────────────┐  │ │ │
│  │          │  │ │img│ name + timestamp              │  │ │ │
│  │          │  │ │   │ message text                  │  │ │ │
│  │          │  │ └───┴──────────────────────────────┘  │ │ │
│  │          │  └───────────────────────────────────────┘ │ │
│  │          ├───────────────────────────────────────────┤ │
│  │          │  Input form (border-t, flex)               │ │
│  └──────────┴───────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

### Responsywne breakpoints

| Breakpoint | Min-width | Zachowanie |
|------------|-----------|------------|
| `sm` | 40rem (640px) | Zwiększone paddingi, 2-kolumnowe gridy |
| `md` | 48rem (768px) | Tablety |
| `lg` | 64rem (1024px) | Sidebar agentów widoczny (`lg:block`) |

Poniżej `lg` sidebar chowa się (hamburger lub slide).

## Elevation & Depth

| Poziom | Shadows | Użycie |
|--------|---------|--------|
| 0 | `none` | tła, panele |
| 1 | `shadow-sm` (0 1px 2px 0 rgb(0 0 0 / 0.05)) | containery, cards |
| 2 | `shadow-md` | modale, dropdowny |
| 3 | `shadow-lg` | toasty, fixed elements |

## Shapes

| Token | Wartość | Użycie |
|-------|---------|--------|
| `rounded-full` | `9999px` | awatary, badge, status dots |
| `rounded-xl` | `12px` | główny container workspace |
| `rounded-lg` | `8px` | inputy, cards, buttony |
| `rounded-md` | `6px` | hash tab pills, tagi |

## Components

### Sidebar (agent list)
- `w-64`, `border-r`, `border-[#E8EAED]`
- Header: "Zespół" (xs, uppercase, tracking-wider)
- Agent item: `flex gap-3 px-4 py-2 hover:bg-[#f8f9fa]`
- Avatar: 32px × 32px, `rounded-full`
- Status dot: 10px (w-2.5 h-2.5), `rounded-full`, `border-2 border-white`, `absolute -bottom-0.5 -right-0.5`
- Animacja: `animate-pulse-dot`
- Name: `text-sm font-medium truncate`
- Role: `text-xs text-secondary truncate`

### Hash tab bar
- Poziomy scroll (`overflow-x-auto`, `scrollbar-none`)
- Pill: `px-2 sm:px-3 py-1.5 rounded-md text-[11px] sm:text-xs font-medium whitespace-nowrap`
- Icon: unicode `text-[10px]`
- Default: `text-secondary hover:bg-alt hover:text-primary`
- Active: `bg-[#E8F0FE] text-accent`
- Transition: `transition-colors`

### Chat message
- Container: `flex gap-3 py-3 animate-fade-slide-in`
- Avatar: 28px × 28px, `rounded-full`, `pt-0.5`
- Header: agent name (sm, font-medium) + timestamp (xs, secondary)
- Body: `text-sm leading-relaxed text-secondary`
- First-party (AO): `font-medium text-accent` dla ostatniego call-to-action

### Input form
- Container: `border-t border-light`, `px-4 lg:px-6 py-4`
- Flex: `flex gap-2`
- Input: `flex-1 px-4 py-2.5 text-sm border border-[#DADCE0] rounded-lg bg-white`
- Focus: `outline-none focus:border-accent focus:ring-1 focus:ring-accent`
- Submit: `px-5 py-2.5 text-sm font-medium text-white bg-accent rounded-lg hover:bg-[#1765CC] disabled:opacity-50 disabled:cursor-not-allowed`

### Scrollbar customization
- Thin: `.scrollbar-thin` (cienki scrollbar dla sidebar)
- None: `.scrollbar-none` (dla tab bar)

## Animacje

| Name | Trigger | Opis |
|------|---------|------|
| `fade-slide-in` | nowa wiadomość w feed | wejście z dołu + fade |
| `pulse-dot` | status agenta | pulsowanie (obecny/żywy) |

## Do's and Don'ts

- **Do:** Używaj spójnych radiusów według hierarchii (full → xl → lg → md)
- **Do:** Utrzymuj wysoki kontrast tekst/tło (primary vs secondary scale)
- **Do:** Stosuj disabled stany z opacity-50 + cursor-not-allowed
- **Do:** Zachowaj `transition-colors` na wszystkich interaktywnych elementach
- **Don't:** Nie mieszaj systemów radius — wszystkie buttony rounded-lg, nie część rounded-md
- **Don't:** Nie pomijaj focus ring — `focus:outline-none focus:ring-1 focus:ring-accent`
- **Don't:** Nie używaj emoji zamiast unicode symboli w hash tabach
