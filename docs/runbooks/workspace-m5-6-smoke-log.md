<link rel="stylesheet" href="../styles/main.css">

# M5.6 — 3-day smoke log (CEO sign-off)

[← M1 server runbook](workspace-m1-server-mode.md) · [M5.6 plan](../planning/workspace-mvp-m5-6-m1-server-mode.md)

**Owner:** CEO · **Checker:** backend-team (automation) · **Close when:** 3 consecutive days PASS (warnings OK until calendar granted)

---

## Daily command (from M5)

```bash
cd ~/Developer/Repositories/octadecimal-agents/octadecimal.pro
./scripts/octa workspace smoke --remote m1-ceo
```

After granting **Calendars** on M1, re-run with strict mode:

```bash
./scripts/octa workspace smoke --remote m1-ceo --strict-calendar
```

Optional UI check on M1: `./scripts/octa workspace open`

### Bez Twojej uwagi (automatyzacja M5 → M1)

```bash
# Cron codziennie 09:00 — smoke + wpis do tabeli poniżej
./scripts/install-m5-m1-smoke-cron.sh

# Jednorazowy run + odświeżenie tabeli
OCTA_SMOKE_UPDATE_DOC=1 ./scripts/octa-m1-smoke-daily.sh
```

Logi maszynowe: `~/.octa/logs/m5-6-m1-smoke.log` (czytelny), `m5-6-m1-smoke.jsonl` (JSONL).

---

## Log

| Day | Date | Result | calendar_source | Notes |
|-----|------|--------|-----------------|-------|
| 1 | 2026-06-15 | PASS+w | fixture-denied | auto M5→M1; calendar pending |
| 2 | | | | cron 09:00 M5 |
| 3 | | | | cron 09:00 M5 |

---

## Calendar permission (one-time on M1)

1. Open lid, log in as CEO (or use existing session)
2. `./scripts/octa workspace open` → `#Planning`
3. Approve macOS **Calendars** prompt — see [macos-calendar-permissions.md](macos-calendar-permissions.md)
4. Re-run smoke until `calendar_source` is `macos` or `calctl`

---

## Failover exercise (M5.6.5 — optional)

| Step | Action | Expected |
|------|--------|----------|
| 1 | Confirm M1 health via SSH | `curl :8042/workspace/health` OK |
| 2 | Reboot M1 (AC power) | After 2–3 min, health OK without manual start |
| 3 | Closed-lid test (optional) | See runbook §13 — SSH health OK with lid closed |

Check when done: [ ] failover exercise completed

---

## Sign-off

- [ ] 3× daily smoke PASS logged
- [ ] Calendar live (`--strict-calendar` PASS) OR documented defer with fixture + reason
- [ ] Reboot test OK
- [ ] backend-team updates SYNC-M16 in triple-track + dashboard

**Signed:** _________________ **Date:** ___________
