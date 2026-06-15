<link rel="stylesheet" href="../styles/main.css">

# Phase M5.5 — Complete M5 dev loop

[← Workspace MVP roadmap](workspace-mvp-roadmap.md) · [ADR 006](../adr/006-m5-only-dev-strategy.md) · [Workspace MVP](../architecture/workspace-mvp.md)

**Status:** todo · **Estimate:** ~1 week · **Priority:** P0 (next)

## Goal

Make the M5 localhost loop **operationally complete** for daily CEO use — without prod deploy, Ubuntu integration, or HYDRA. A new developer (or future you) can run Workspace every day with documented automation and consistent naming.

---

## Starting point

M5.1–M5.4 delivered: CI E2E, full T1 RAG, AO evals, MCP read-only tools, launchd for **knowledge sync** only. Gaps: no launchd for Workspace API, board teams still use legacy Ubuntu names, no consolidated daily runbook, Kanon sign-off v1 only covers Sprint MVP.

---

## Tasks

| ID | Task | Description | Done when |
|----|------|-------------|-----------|
| M5.5.1 | Daily dev runbook | ✅ [workspace-daily-dev.md](../runbooks/workspace-daily-dev.md) | |
| M5.5.2 | launchd for Workspace API | ✅ `install-workspace-api-launchd.sh` + plist template | |
| M5.5.3 | Board team rename | `ledger.py` teams → Octa-native (e.g. `platform`, `knowledge`, `ops`, `product`) | seed + UI + tests updated |
| M5.5.4 | Kanon sign-off v2 | Extend §10 checklist in Knowledge for M5.2–M5.4 | all items PASS on clean M5 |
| M5.5.5 | README polish | `README.md` + architecture: M5-only scope, link ADR 006 | onboarding < 15 min |

---

## Architecture (unchanged)

```text
M5 Mac (localhost only)
├── Workspace :8042
├── Qdrant dev :6335 → knowledge_chunks_dev
├── SQLite ledger + approvals
├── launchd: knowledge sync (existing) + Workspace API (new)
└── KNOWLEDGE_ROOT local clone
```

No pc-ubuntu, no Tailscale prod push in this phase.

---

## Risks

| Risk | Mitigation |
|------|------------|
| launchd port conflicts | Document stop/start; use same ports as `octa-mvp-up.sh` |
| Team rename breaks E2E | Update fixtures and golden data in one PR |
| Scope creep into M5.6 | M1 server mode is separate phase |

---

## Phase completion criteria

- [x] Daily runbook reviewed on clean M5
- [x] launchd Workspace API survives reboot
- [ ] Board teams Octa-native in code + docs
- [ ] Kanon sign-off v2 checked in Knowledge
- [ ] pytest + E2E green in CI

---

## Related

- [M5.6 — M1 server mode](workspace-mvp-m5-6-m1-server-mode.md)
- [Knowledge sync runbook](../runbooks/knowledge-embed-sync-schedule.md)
- [Daily dev runbook](../runbooks/workspace-daily-dev.md)
