<link rel="stylesheet" href="../styles/main.css">

# Phase M5.7 — Ubuntu hosting only (deferred)

[← Workspace MVP roadmap](workspace-mvp-roadmap.md) · [ADR 006](../adr/006-m5-only-dev-strategy.md)

**Status:** deferred · **Estimate:** 2–3 weeks · **Priority:** P2 (after M5.6)

## Goal

Provide **hosting infrastructure** on pc-ubuntu: prod Qdrant backup, HTTPS access, auth — **without** HYDRA agent orchestration or integration with legacy Ubuntu dev-teams. Workspace logic stays in `octadecimal.pro`; Ubuntu is a **semantic + relay** node only.

This phase absorbs the infrastructure slice from the former [M5.5 prod bridge](workspace-mvp-m5-5-prod-bridge.md).

---

## What this phase includes

| ID | Task | Description |
|----|------|-------------|
| M5.7.1 | Push embed → pc-ubuntu | `embed-knowledge sync --prod` via Tailscale → Qdrant `:6333` |
| M5.7.2 | Prod/dev collections | `knowledge_chunks` vs `knowledge_chunks_dev` runbook |
| M5.7.3 | HTTPS subdomain | `workspace.octadecimal.pro` — proxy only, no HYDRA UI |
| M5.7.4 | Auth layer | basic auth / OAuth2 proxy; no public open CEO panel |
| M5.7.5 | Backup & restore | Qdrant snapshot + ledger backup runbook |
| M5.7.6 | PostgreSQL path (optional) | Spike with [Phase 5](phase-5-async-persistence-audit.md) |

---

## What this phase excludes

- HYDRA n8n workflows as Octa orchestration center
- Legacy Ubuntu dev-teams (`automation`, `security`, etc.) on Board
- Twenty CRM integration
- Agent fleet management on Ubuntu

HYDRA remains **archive reference** on pc-ubuntu; Octa kernel is `octadecimal.pro` on Mac.

---

## Target architecture

```text
CEO browser ── HTTPS ──► workspace.octadecimal.pro
                              │
                              ▼
                    pc-ubuntu (hosting only)
                    ├── Qdrant :6333 → knowledge_chunks
                    ├── nginx reverse proxy + auth
                    └── optional: relay to M1/M5 Workspace API

M5/M1 (dev) ── embed-knowledge push ──► Qdrant prod
```

---

## Collection separation

| Env | Qdrant | Collection | CLI |
|-----|--------|------------|-----|
| Dev M5 | `:6335` | `knowledge_chunks_dev` | `sync --dev` |
| Prod pc-ubuntu | `:6333` | `knowledge_chunks` | `sync --prod` |

**Rule:** never write dev → prod without explicit `--prod` flag.

---

## Phase completion criteria

- [ ] Prod Qdrant synced with T1 Kanon
- [ ] Operational runbook for collections
- [ ] HTTPS subdomain with auth
- [ ] Backup/restore exercise documented
- [ ] No HYDRA agent dependencies in Workspace path

---

## Related

- [Former M5.5 prod bridge doc](workspace-mvp-m5-5-prod-bridge.md) (superseded)
- [ADR 004 — SQLite dev, Postgres prod](../adr/004-sqlite-dev-postgres-prod.md)
- Knowledge: `knowledge-embeddings.md`
