# ADR 006: M5-only development strategy

**Status:** accepted  
**Date:** 2026-06-15  
**Context:** Octa Workspace MVP M5.1–M5.4

## Context

After M5.1–M5.4, Workspace runs reliably on localhost M5: chat AO, RAG, Board, HITL, MCP read-only tools, and dev Qdrant (`:6335`). The original roadmap treated **M5.5** as a production bridge to pc-ubuntu / HYDRA (`embed-knowledge push`, subdomain, fleet integration).

Implementation has **not incurred losses** on the current path. Integrating with legacy Ubuntu dev-teams and HYDRA orchestration now would expand scope without improving the daily CEO loop on Mac.

## Decision

1. **Development stays M5-only** until the local dev loop is complete (M5.5).
2. **M5.5** reframed: runbooks, launchd for API, Octa-native board team names, Kanon sign-off v2 — not prod deploy.
3. **M5.6** (new): **M1 server mode** — always-on agents on the daily-driver Mac.
4. **M5.7** (deferred): **pc-ubuntu hosting only** — backup, HTTPS, prod Qdrant — **no** HYDRA agent fleet or Ubuntu team orchestration.
5. **M6 platform** (phases 5–13) continues **in parallel** with M5 work.

## Explicitly deferred

| Item | Reason |
|------|--------|
| `embed-knowledge sync --prod` to pc-ubuntu | Hosting phase M5.7; dev loop first |
| HYDRA fleet / n8n integration as Octa center | HYDRA remains archive reference |
| Legacy Ubuntu dev-teams on Board | Octa-native team names on M5 |
| UX.6 `#Dev` / git / CRM panels | Needs separate product decision |

## Node roles (target)

| Node | Role |
|------|------|
| **M5** | Dev/build: octadecimal.pro, embed sync `--dev`, tests |
| **M1** | Daily driver + **server mode** (M5.6): always-on Workspace/agents |
| **pc-ubuntu** | **Hosting only** (M5.7): Qdrant prod backup, HTTPS, optional static relay — not agent orchestration |

## Consequences

- Roadmap docs updated: [workspace-mvp-roadmap.md](../planning/workspace-mvp-roadmap.md).
- Old [M5.5 prod bridge](../planning/workspace-mvp-m5-5-prod-bridge.md) superseded by M5.5 + M5.7.
- [ADR 002](002-mcp-compose-strategy.md): multi-server MCP compose deferred to M5.7+, not M5.5.
- Knowledge Kanon (PL) section 9 updated to match this sequence.

## Related

- [Workspace MVP architecture](../architecture/workspace-mvp.md)
- Knowledge: `octa-os/mvp-localhost-m5.md`, `OCTA-ZALOZENIA.md`
