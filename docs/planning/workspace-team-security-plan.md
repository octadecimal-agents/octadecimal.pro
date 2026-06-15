<link rel="stylesheet" href="../styles/main.css">

# Plan wdrożenia — security-team

[← Triple-track](workspace-mvp-triple-track.md) · [M5.8 Security Ops](workspace-mvp-m5-8-security-ops.md)

**Zespół:** security-team · **Framework:** Cursor *(alternatywa: OpenCode + BMAD)* · **Gałęzie:** `feat/sec-*`  
**Orkiestracja:** M1 24/7 · **Wykonanie:** pc-ubuntu (+ M1 self) przez SSH  
**Kanon PL:** `Knowledge/01-Base-Point/pro/projects/octa-os/plany/zespol-security-plan.md`

---

## Misja

Odczyt raportów audytu (Lynis, octa audit), automatyczna remediacja tier 0–1, eskalacja tier 2+ do CEO przez `#Review`, instrukcje runbook dla tier 3. **Agenci na M1**, **nie** flota na pc-ubuntu (ADR 006).

Mail: `security@octadecimal.pl`

---

## Faza 0 — Fundament audytu ✅

### pc-ubuntu

- [x] `octa-pc-ubuntu-security-audit.sh` — raport dzienny + progi legacy
- [x] Instalacja w `/usr/local/bin/` + symlink `system-monitor.sh`
- [x] Cron `/etc/cron.d/octa-pc-ubuntu-security-audit`
- [x] Sudo watch + `/var/log/octa-sudo.log`
- [x] Runbook [pc-ubuntu-security-audit.md](../runbooks/pc-ubuntu-security-audit.md)
- [x] Test email `--test-email` działa (msmtp root)
- [x] Lynis 3.0.9 — pierwszy audyt (Hardening Index 58)

### M1

- [x] `octa-m1-security-audit.sh` + runbook
- [x] LaunchDaemons daily + sudo watch (do weryfikacji install na M1)

### Dokumentacja

- [x] Knowledge: `servers/pc-ubuntu/Skrypty.md` — sekcja audytu
- [ ] Knowledge: hub triple-track + ten plan (PL mirror)

---

## Faza 1 — M5.8 Security Ops (SEC.1–SEC.3) 🔲

**Dokument:** [workspace-mvp-m5-8-security-ops.md](workspace-mvp-m5-8-security-ops.md)  
**Estymata:** 2–3 tygodnie · **Zależność:** M5.6 (Workspace M1 24/7) dla SEC.2

### SEC.1 Polityka remediacji

- [ ] `security-policy.yaml` w repo — mapowanie Lynis ID → tier 0/1/2/3
- [ ] Tier 0: auto (apt security upgrade, purge packages, docker prune)
- [ ] Tier 1: auto + notify CEO (restart usługi, wyłączenie avahi/cups)
- [ ] Tier 2: HITL CEO (`#Review`)
- [ ] Tier 3: runbook only (LUKS, GRUB, runlevel)
- [ ] pytest walidacji polityki

### SEC.2 Agenci na M1

- [ ] Agent **Triage** — parse Lynis + octa audit report
- [ ] Agent **Remediator** — tier 0–1 via SSH
- [ ] Agent **Advisor** — tier 3 runbook markdown
- [ ] Cron/launchd: pull raportów pc-ubuntu → M1 (`/var/log/octa/` lub rsync)
- [ ] Integracja z Workspace API (trigger po raporcie)

**Sync:** SYNC-M16 — wymaga M5.6 health OK na M1.

### SEC.3 HITL remediacja tier 2+

- [ ] Tworzenie `ApprovalRequest` z opisem + rollback
- [ ] CEO approve → `pc-ubuntu-run.sh` / Bitwarden grant → exec
- [ ] CEO reject → log + wpis Board (`team=ops`)
- [ ] Test E2E flow: raport → Review → approve → log remediacji

**Sync:** SYNC-HITL — Review API od backend-team ✅.

---

## Faza 2 — SEC.4 Executor na pc-ubuntu 🔲

- [ ] `/usr/local/bin/octa-security-exec.sh` — allowlist komend
- [ ] Mapowanie `PKGS-7392` → `apt upgrade` security
- [ ] Mapowanie SSH hardening → odrzucone bez tokenu HITL
- [ ] Log `/var/log/octa/security-exec.log`
- [ ] Unit tests bash

---

## Faza 3 — SEC.5 Lynis automation 🔲

- [ ] Lynis weekly cron (niedziela 05:00 UTC)
- [ ] Sekcja Lynis summary w mailu octa audit
- [ ] Archiwum `/var/log/lynis/` + Hardening Index w subject

---

## Faza 4 — SEC.6 Docker / CVE 🔲

- [ ] Docker Bench Security — weekly
- [ ] Trivy scan obrazów — critical/high count w raporcie
- [ ] Tier mapping CVE critical → HITL

---

## Faza 5 — SEC.7 Evals i hardening ciągły 🔲

- [ ] Eval: agent nie eskaluje tier 0 do HITL
- [ ] Eval: agent nie wykonuje tier 2 bez approve
- [ ] Eval: rollback documented for tier 2 actions
- [ ] Integracja Lynis trend (Hardening Index w czasie)

---

## Backlog remediacji (z Lynis 2026-06-15)

Priorytet CEO / tier — do przypisania w `security-policy.yaml`:

| Temat | Lynis / źródło | Sugerowany tier |
|-------|----------------|-----------------|
| Podatne pakiety | PKGS-7392 | 0 — auto |
| x11vnc / avahi / cups | BOOT / manual | 1 — auto + notify |
| SSH hardening | SSH-7408 | 2 — HITL |
| nginx SSL | HTTP-6710 | 2 — HITL |
| GRUB password | BOOT-5122 | 3 — runbook |
| LUKS / encryption | DEB-0001 | 3 — runbook |
| nopasswd-temp sudoers | manual | 2 — HITL (usuń jeśli martwy) |

---

## Zasady postępowania

1. **Orkiestracja na M1** — nigdy pełna autonomia agenta z sudo na pc-ubuntu 24/7.
2. **Grant sudo** — `pc-ubuntu-grant.sh` przed remediacją, `revoke` po operacji.
3. **Tier 0 tylko z policy** — rozszerzenia wymagają PR + review CEO.
4. **Ownership:** `scripts/octa-*-security*`, `security-policy.yaml`, runbooki security.
5. **Nie dotykaj** `static/`, `router.py` bez WO do backend-team.
6. **HITL obowiązkowy** dla: SSH, nginx, firewall, sudoers, usunięcie usług produkcyjnych.
7. **Log wszystkiego** — `/var/log/octa/`, mail do security@, opcjonalnie Board ops.

---

## Prompt inicjacyjny (copy-paste → Cursor)

```text
Zespół: security-team
Repo: octadecimal.pro
Framework: Cursor
Host operacyjny: M1 (Workspace 24/7 po M5.6)
Cele remediacji: pc-ubuntu (192.168.0.101), M1 self-audit

Przeczytaj obowiązkowo:
- docs/planning/workspace-mvp-triple-track.md (macierz SYNC-*)
- docs/planning/workspace-team-security-plan.md (ten dokument)
- docs/planning/workspace-mvp-m5-8-security-ops.md
- docs/runbooks/pc-ubuntu-security-audit.md
- docs/runbooks/m1-security-audit.md
- Knowledge: 01-Base-Point/pro/projects/octa-os/plany/zespol-security-plan.md

Kontekst Lynis pc-ubuntu (2026-06-15): Hardening Index 58.
Krytyczne: PKGS-7392 (CVE), x11vnc, SSH hardening, nginx SSL.

Twoja misja (faza bieżąca): SEC.1 security-policy.yaml + szkielet SEC.2 agent Triage.

NIE dotykaj:
- src/.../workspace/static/ (frontend-team)
- router.py bez WO (backend-team)
- UX / design-artifacts

Remediacja pc-ubuntu:
- Knowledge/tools/sudo/pc-ubuntu-grant.sh → run → revoke
- Nigdy NOPASSWD permanent bez ADR

HITL tier 2+:
- ApprovalRequest → CEO #Review → dopiero exec

Branch: feat/sec-policy-yaml (lub feat/sec-*)
PR: [security-team] + pytest jeśli dotyczy

Weryfikacja lokalna:
- bash -n scripts/*.sh
- pytest tests/unit/scripts/test_octa_* jeśli istnieją

Dashboard CEO (Knowledge) — po każdym slice / bloker / SYNC:
- edytuj WYŁĄCZNIE sekcję TEAM:security w:
  Knowledge/01-Base-Point/pro/projects/octa-os/triple-track-dashboard.md
- ustaw: postęp % fazy SEC.*, następny milestone, bloker, datę aktualizacji
- zaktualizuj pasek M5.8 w sekcji GLOBAL; po SEC.3 → SYNC-HITL 🟢
- nie edytuj sekcji backend/frontend; commit: dashboard(triple-track): [security-team] …
- szczegóły checkbox → workspace-team-security-plan.md (SSOT)
```

---

## Prompt inicjacyjny — alternatywa (OpenCode + BMAD)

Użyj, gdy security-team pracuje w **OpenCode** z metodologią BMAD (spec → investigate → dev → review). Ten prompt **różni się** od Cursor: wymusza workflow BMAD, artefakty w repo i jawne tiering przed remediacją.

```bash
cd octadecimal.pro
opencode
```

**Kickoff (copy-paste do OpenCode):**

```text
Zespół: security-team
Repo: octadecimal.pro
Framework: OpenCode + BMAD Method
Host operacyjny: M1 (Workspace 24/7 po M5.6)
Cele remediacji: pc-ubuntu (192.168.0.101), M1 self-audit

Przeczytaj obowiązkowo (repo + Knowledge):
- docs/planning/workspace-mvp-triple-track.md — macierz SYNC-HITL, SYNC-M16, SYNC-SEC-*
- docs/planning/workspace-team-security-plan.md (ten dokument)
- docs/planning/workspace-mvp-m5-8-security-ops.md
- docs/runbooks/pc-ubuntu-security-audit.md
- docs/runbooks/m1-security-audit.md
- Knowledge/01-Base-Point/pro/projects/octa-os/plany/zespol-security-plan.md
- Knowledge/01-Base-Point/pro/servers/pc-ubuntu/agents-knowledge/security-audit-checklist.md

Kontekst Lynis pc-ubuntu (2026-06-15): Hardening Index 58.
Warnings: PKGS-7392 (podatne pakiety), TIME-3185 (NTP).
Priorytet remediacji: PKGS-7392 → tier 0, x11vnc/avahi → tier 1, SSH/nginx → tier 2 (HITL).

Workflow BMAD (kolejność obowiązkowa):
1. /bmad-investigate — triage raportu Lynis + octa audit; wynik: lista findingów z tier 0–3
2. /bmad-spec — SEC.1: distil security-policy.yaml (Lynis control ID → tier → allowed_action)
3. /bmad-quick-dev — implementacja policy + szkielet agenta Triage (tylko feat/sec-*)
4. /bmad-code-review — adversarial review PR przed merge (czy tier 2 nie wykona się bez HITL)
5. Opcjonalnie: /bmad-review-edge-case-hunter — edge cases grant sudo, pusty auth.log, pipefail
6. Opcjonalnie: /bmad-testarch-nfr — audyt NFR (security, reliability) po SEC.4

Komendy OpenCode (ścieżki): .opencode/commands/bmad-*.md

NIE dotykaj:
- src/.../workspace/static/ (frontend-team)
- router.py bez Work Order → backend-team (SYNC-HITL)
- design-artifacts/ (frontend-team)

Remediacja pc-ubuntu (tylko po tier assignment w policy):
- Knowledge/01-Base-Point/tools/sudo/pc-ubuntu-grant.sh
- wykonanie → pc-ubuntu-revoke.sh (zawsze)
- tier 0–1: auto po policy; tier 2+: ApprovalRequest → CEO #Review → dopiero exec

Output artefaktów (przed kodem):
- security-artifacts/m5.8/investigate-lynis-20260615.md (findings + tier)
- security-policy.yaml (repo root lub config/security/)
- security-artifacts/m5.8/work-order-sec2-triage-agent.md (handoff SEC.2)

Branch: feat/sec-policy-yaml
PR: [security-team] — bash -n scripts/*.sh + pytest tests/unit/scripts/test_octa_*

Metodologia: mały slice (1 SEC.* na PR), checkboxy w workspace-team-security-plan.md po merge.

Dashboard CEO (Knowledge) — po każdym slice / bloker / SYNC:
- edytuj WYŁĄCZNIE sekcję TEAM:security w Knowledge/.../triple-track-dashboard.md
- postęp %, milestone, bloker, pasek M5.8 w GLOBAL; SYNC-HITL 🟢 po SEC.3
- commit: dashboard(triple-track): [security-team] …; nie edytuj backend/frontend
```

**Mapowanie faz SEC → BMAD:**

| Faza | Komenda BMAD | Cel |
|------|--------------|-----|
| SEC.1 | `/bmad-spec` | `security-policy.yaml` jako kontrakt maszynowy |
| SEC.2 triage | `/bmad-investigate` | Parse Lynis + przypisanie tier |
| SEC.2–4 implementacja | `/bmad-quick-dev` | skrypty, agent, executor |
| SEC.7 evals | `/bmad-testarch-nfr` + `/bmad-code-review` | brak fałszywej eskalacji HITL |
| Po remediacji | `/bmad-retrospective` | lessons learned (opcjonalnie) |

---

## Powiązane

- [Triple-track](workspace-mvp-triple-track.md)
- [M5.8 Security Ops](workspace-mvp-m5-8-security-ops.md)
- [pc-ubuntu security audit runbook](../runbooks/pc-ubuntu-security-audit.md)
- [M1 security audit runbook](../runbooks/m1-security-audit.md)
- Knowledge: `tools/sudo/pc-ubuntu-*.sh`
- Legacy agent mirror: `Knowledge/.../pc-ubuntu/devops-team/.claude/agents/security-agent.md`
- OpenCode BMAD: `.opencode/commands/bmad-investigate.md`, `bmad-spec.md`, `bmad-quick-dev.md`, `bmad-code-review.md`

---

## Historia

| Data | Zmiana |
|------|--------|
| 2026-06-15 | Utworzenie planu security-team (triple-track) |
| 2026-06-15 | Lynis baseline pc-ubuntu — Index 58 |
