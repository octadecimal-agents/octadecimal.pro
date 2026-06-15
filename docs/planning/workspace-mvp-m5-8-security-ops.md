<link rel="stylesheet" href="../styles/main.css">

# Phase M5.8 — Security Ops (security-team)

[← Roadmap](workspace-mvp-roadmap.md) · [Triple-track](workspace-mvp-triple-track.md) · [Security team plan](workspace-team-security-plan.md)

**Status:** planning · **Estimate:** 2–3 weeks · **Priority:** P1 (parallel) · **Owner:** security-team

---

## Goal

Automated security operations loop: **collect reports** (pc-ubuntu + M1) → **triage** (Lynis + octa audit) → **remediate** tier 0–1 → **HITL CEO** tier 2+ → **runbook** tier 3.

**Control plane:** M1 (Workspace agents 24/7).  
**Data plane:** pc-ubuntu (SSH + allowlist executor).  
**No** agent fleet on Ubuntu (ADR 006).

---

## Dependencies

| Dependency | Provider | Status |
|------------|----------|--------|
| Review HITL API | backend-team | ✅ |
| pc-ubuntu audit scripts | security-team | ✅ |
| M1 audit scripts | security-team | ✅ |
| Workspace 24/7 M1 | backend-team M5.6 | 🔄 |
| Bitwarden sudo grant | Knowledge tools | ✅ |

---

## Deliverables

| ID | Task | Acceptance |
|----|------|------------|
| SEC.1 | `security-policy.yaml` | Lynis IDs mapped to tiers; pytest |
| SEC.2 | Triage + Remediator agents on M1 | Parse report; tier 0 dry-run |
| SEC.3 | HITL integration tier 2+ | E2E: report → Review → exec |
| SEC.4 | `octa-security-exec.sh` allowlist | Only whitelisted commands run |
| SEC.5 | Lynis weekly cron + mail section | Hardening Index in report |
| SEC.6 | Docker Bench + Trivy (optional) | CVE count in weekly mail |
| SEC.7 | Evals (no false escalation) | CI or script gate |

---

## Architecture

```text
pc-ubuntu                          M1
├── cron: octa audit daily         ├── launchd/cron: pull reports
├── cron: lynis weekly             ├── Agent Triage
├── octa-security-exec.sh          ├── Agent Remediator (tier 0-1)
└── logs → rsync/scp ─────────────►├── Agent Advisor (tier 3)
                                   ├── Review HITL (tier 2)
                                   └── SSH → pc-ubuntu-run.sh
```

---

## Sync points

See [triple-track §3](workspace-mvp-triple-track.md#3-punkty-synchronizacji-między-zespołami):

- **SYNC-HITL** — tier 2+ approvals
- **SYNC-M16** — SEC.2 blocked until M5.6 smoke OK
- **SYNC-SEC-EXEC** — executor install on pc-ubuntu

---

## Out of scope (M5.8)

- Full Wazuh/SIEM
- OpenSCAP formal compliance reports
- Replacing fail2ban/rkhunter
- HYDRA n8n orchestration

---

## Related

- [pc-ubuntu security audit runbook](../runbooks/pc-ubuntu-security-audit.md)
- [m1 security audit runbook](../runbooks/m1-security-audit.md)
