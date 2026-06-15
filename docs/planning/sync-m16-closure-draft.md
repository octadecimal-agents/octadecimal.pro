<link rel="stylesheet" href="../styles/main.css">

# SYNC-M16 — draft zamknięcia (backend-team)

[← Triple-track §3.3](workspace-mvp-triple-track.md#33-sync-m16--backend--security--frontend) · [Smoke log](../runbooks/workspace-m5-6-smoke-log.md)

**Status:** 🔴 **DRAFT — nie publikować** dopóki CEO nie podpisze smoke log.  
**Aktywacja:** po sign-off CEO → przenieś treść §2 do triple-track §3.3 i ustaw SYNC-M16 🟢 w dashboardzie.

---

## 1. Kryteria zamknięcia (checklist)

| Gate | Wymagane | Stan |
|------|----------|------|
| M5.6.1 launchd | health OK po reboot M1 | ⏳ CEO reboot test |
| M5.6.3 kalendarz | `#Planning` live (`macos`/`calctl`) | ⏳ Calendars permission |
| Smoke 3 dni | 3× PASS w smoke log | ⏳ dzień 1 ✅; 2–3 cron |
| M5.6.5 failover | reboot bez ręcznego startu | ⏳ CEO |
| API stabilne | brak breaking change od M5.5 | ✅ |

---

## 2. Tekst do wklejenia w triple-track §3.3 (po sign-off)

```markdown
### 3.3 SYNC-M16 — **ZAMKNIĘTE** (DATA_SIGNOFF)

**M5.6 server mode verified on physical M1.**

| Consumer | Odblokowane |
|----------|-------------|
| **security-team** | SEC.2 — agenci Triage/Remediator na M1 (launchd/cron pull raportów) |
| **frontend-team** | UX.4 — Push/Shortcuts M1 (po stabilnym API) |

**Evidence:** [workspace-m5-6-smoke-log.md](../runbooks/workspace-m5-6-smoke-log.md) — signed DATA_SIGNOFF.

**API:** stabilne względem [workspace-mvp.md](../architecture/workspace-mvp.md) — brak nowych endpointów bez WO.
```

---

## 3. Powiadomienia zespołów (copy-paste)

### security-team

```text
SYNC-M16 closed — M1 Workspace 24/7 verified.
Możecie startować SEC.2 (agenci Triage na M1).
Bloker usunięty: health :8042 + LaunchDaemon po reboot.
Plan: docs/planning/workspace-team-security-plan.md SEC.2
```

### frontend-team

```text
SYNC-M16 closed — M1 always-on OK.
UX.4 (Push/Shortcuts M1) odblokowane po Waszym UX.1–UX.3 backlogu.
API stable — SYNC-API bez zmian breaking.
Plan: docs/planning/workspace-team-frontend-plan.md UX.4
```

---

## 4. Dashboard (Knowledge)

Po sign-off zaktualizuj `Knowledge/.../triple-track-dashboard.md`:

- SYNC-M16 → 🟢
- backend postęp M5.6 → 100%
- security bloker SEC.2 → usunąć
- frontend SYNC-UX4 → odblokowany w opisie

Commit: `dashboard(triple-track): [backend-team] SYNC-M16 closed`

---

## 5. Historia

| Data | Zdarzenie |
|------|-----------|
| 2026-06-15 | Draft utworzony; dzień 1 smoke PASS+w; cron M5 zainstalowany |
