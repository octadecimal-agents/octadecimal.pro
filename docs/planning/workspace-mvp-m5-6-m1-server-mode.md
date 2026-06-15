<link rel="stylesheet" href="../styles/main.css">

# Phase M5.6 — M1 server mode

[← Workspace MVP roadmap](workspace-mvp-roadmap.md) · [ADR 006](../adr/006-m5-only-dev-strategy.md)

**Status:** planned · **Estimate:** 1–2 weeks · **Priority:** P1 (after M5.5)

## Goal

Run Workspace and agents **24/7 on M1** (daily-driver Mac) so the CEO does not manually start `octa-mvp-up.sh` on M5 for routine use. M5 remains the **build/test** node; M1 becomes the **always-on** consumption node.

---

## Starting point

After M5.5: documented dev loop, launchd on M5, stable localhost API. M1 currently has no persistent Workspace process.

---

## Target architecture

```text
M1 (macOS — daily driver, server mode)
├── launchd: Workspace API + static UI (or proxy to M5 dev)
├── Ollama optional (light models)
├── MCP macOS adapters (calendar live)
└── Tailscale client → M5 / pc-ubuntu (future M5.7 only)

M5 (dev/build)
├── git, pytest, embed-knowledge sync --dev
└── optional: remote API for M1 during active dev
```

**Principle:** agents and CEO UI live where the CEO works (M1). M5 is for implementation and CI.

---

## Tasks (draft)

| ID | Task | Description | Done when |
|----|------|-------------|-----------|
| M5.6.1 | M1 launchd stack | Install plist(s) for Workspace on M1 | health OK after reboot |
| M5.6.2 | Network binding | Document `127.0.0.1` vs Tailscale LAN; no public exposure | runbook |
| M5.6.3 | Calendar on M1 | `CALENDAR_PROVIDER=auto` on daily driver | `#Planning` live events |
| M5.6.4 | Shortcuts / CLI entry | Optional `octa workspace open` from M1 | one-command CEO start |
| M5.6.5 | Failover doc | When M5 dev overwrites API — how M1 degrades | runbook section |

---

## Out of scope

- pc-ubuntu deploy (M5.7)
- HYDRA / Ubuntu dev-teams
- Public HTTPS subdomain

---

## Phase completion criteria

- [ ] Workspace reachable on M1 without manual terminal start
- [ ] Calendar + chat smoke on M1 for 3 consecutive days
- [ ] Runbook: M1 server mode install + rollback

---

## Related

- [M5.5 — M5 dev loop complete](workspace-mvp-m5-5-m5-complete.md)
- [M5.7 — Ubuntu hosting only](workspace-mvp-m5-7-hosting-only.md)
- Knowledge: `OCTA-ZALOZENIA.md` §6 node roles
