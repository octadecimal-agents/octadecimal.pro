<link rel="stylesheet" href="../styles/main.css">

# M5.6 — checklist CEO (~20 min)

[← Smoke log](workspace-m5-6-smoke-log.md) · [M1 server runbook](workspace-m1-server-mode.md)

**Kiedy:** jednorazowo + ewentualnie reboot (~5 min). **Smoke dzień 2–3:** robi cron na M5 o 09:00 — nie musisz pamiętać.

---

## Co już działa bez Ciebie

- LaunchDaemon Workspace na M1 (`:8042`, health OK)
- Codzienny smoke M5 → M1 (cron 09:00 na M5)
- Dzień 1 smoke: **PASS+w** (kalendarz czeka na uprawnienie)
- Skrypty `octa workspace open/smoke` na M1 i M5

---

## Krok 1 — Kalendarz (~1 min) — **automatycznie**

Z **M5** (jednorazowo, wymaga `m1-admin` + sudo na M1):

```bash
cd ~/Developer/Repositories/octadecimal-agents/octadecimal.pro
./scripts/install-m1-calendar-automation.sh --remote m1-admin
```

Albo na **M1** jako admin:

```bash
sudo ./scripts/install-m1-calendar-automation.sh
sudo launchctl kickstart -k system/pl.octadecimal.workspace-api-m1-server
```

To instaluje profil PPPC (Kalendarze dla Pythona) + LaunchAgent odświeżający cache co godzinę. **Bez ręcznego grzebania w Ustawieniach.**

Weryfikacja z M5:

```bash
./scripts/octa workspace smoke --remote m1-ceo --strict-calendar
```

Oczekiwane: `calendar_source=cache` lub `macos`, **PASS**.

---

## Krok 2 — Szybki przegląd UI (~5 min)

Na M1: `http://127.0.0.1:8042/`

| Panel | Sprawdź |
|-------|---------|
| `#Ogolny` | chat odpowiada |
| `#Planning` | widać wydarzenia (nie tylko fixture) |
| `#Review` | kolejka ≥ 1 pozycja |

---

## Krok 3 — Reboot test (~5–10 min)

Na M1 (zasilacz podłączony):

1. Restart Maca (Apple menu → Restart)
2. **Nie** uruchamiaj ręcznie terminala z Workspace
3. Po ~2–3 min z **M5**:

```bash
ssh m1-ceo 'curl -sf http://127.0.0.1:8042/workspace/health | python3 -m json.tool'
./scripts/octa workspace smoke --remote m1-ceo
```

Pass = health `status: ok` bez ręcznego startu.

W smoke log zaznacz: `[x] failover exercise completed` (sekcja M5.6.5).

---

## Krok 4 — Sign-off (~2 min)

Otwórz [workspace-m5-6-smoke-log.md](workspace-m5-6-smoke-log.md):

- [ ] Tabela ma 3 dni PASS (dzień 2–3 uzupełni cron jutro/pojutrze **albo** uruchom ręcznie: `OCTA_SMOKE_UPDATE_DOC=1 ./scripts/octa-m1-smoke-daily.sh`)
- [ ] Kalendarz live (strict smoke OK) **lub** świadomy defer w Notes
- [ ] Reboot test OK
- [ ] Podpis + data na dole pliku

Potem napisz backend-team / agentowi: **„M5.6 sign-off done”** — zamkniemy SYNC-M16 i damy zielone światło SEC.2 + UX.4.

---

## Opcjonalnie (później)

- Puść **frontend** (UX.1 design system) — niezależny od M5.6
- Puść **security** SEC.1 (`security-policy.yaml`) — SEC.2 dopiero po SYNC-M16

---

## Szybkie komendy (M5)

```bash
cd ~/Developer/Repositories/octadecimal-agents/octadecimal.pro
./scripts/octa workspace smoke --remote m1-ceo
tail -3 ~/.octa/logs/m5-6-m1-smoke.log
open docs/runbooks/workspace-m5-6-smoke-log.md
```

Cron wyłączenie: `./scripts/install-m5-m1-smoke-cron.sh --uninstall`
