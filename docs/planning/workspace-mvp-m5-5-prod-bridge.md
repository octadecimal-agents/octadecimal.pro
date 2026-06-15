<link rel="stylesheet" href="../styles/main.css">

# Phase M5.5 — Production bridge (superseded)

[← Workspace MVP roadmap](workspace-mvp-roadmap.md)

**Status:** superseded · **2026-06-15**

This document described a single **M5.5 prod bridge** phase (HYDRA / pc-ubuntu, Qdrant push, subdomain, auth). That plan is **split and reordered** per [ADR 006](../adr/006-m5-only-dev-strategy.md):

| Old concept | New home |
|-------------|----------|
| Complete local dev loop | [M5.5 — M5 dev loop complete](workspace-mvp-m5-5-m5-complete.md) |
| M1 always-on agents | [M5.6 — M1 server mode](workspace-mvp-m5-6-m1-server-mode.md) |
| pc-ubuntu Qdrant, HTTPS, backup | [M5.7 — Ubuntu hosting only](workspace-mvp-m5-7-hosting-only.md) (deferred) |

**Do not implement** HYDRA fleet integration or legacy Ubuntu dev-teams as part of Workspace roadmap.

For historical detail (Qdrant prod/dev tables, nginx auth sketches), see git history of this file or [M5.7](workspace-mvp-m5-7-hosting-only.md).
