# ADR 002 — MCP compose strategy (Workspace M5.4)

**Status:** accepted · **Date:** 2026-06-15 · **Context:** [M5.4 macOS MCP](../planning/workspace-mvp-m5-4-macos-mcp.md)

## Decision

Use **Option A — stub mono-process MCP** for M5:

- Single stdio server: `scripts/octa-mcp-workspace.sh` → `workspace_server.py`
- Read-only tools: calendar, health, wiki, board list, review summary
- Shared read layer: `infrastructure/workspace/read_services.py`

Defer **Option B — multi-server compose** (separate calendar/mail/knowledge MCP) until **[M5.7 hosting only](../planning/workspace-mvp-m5-7-hosting-only.md)** if independent deploy/restart cycles are required. Not part of M5.5 (M5-only dev loop).

## Rationale

| Factor | Mono-process (A) | Multi-server (B) |
|--------|------------------|------------------|
| Dev setup | One Cursor entry | N plist/config entries |
| Policy surface | Single allowlist | Per-server policy |
| Duplication | Shared Python modules | Risk of drift |
| M5 scope | Sufficient for CEO laptop | Overkill before prod |

Option C (Shortcuts host agent) remains out of scope.

## Consequences

- Cursor config stays in `docs/architecture/mcp-workspace.example.json`
- Mail live IMAP and write tools are **not** exposed via MCP in M5.4
- [M5.7](../planning/workspace-mvp-m5-7-hosting-only.md) may split servers if hosting requires independent deploy/restart cycles

## References

- Kanon: `Knowledge/.../research/02-macos-automation-mcp.md`
- Platform: [Faza 10 — MCP](../planning/phase-10-mcp-tool-context.md)
