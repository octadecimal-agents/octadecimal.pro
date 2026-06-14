#!/usr/bin/env bash
# Octa Workspace MCP — calendar + health tools for Cursor (stdio).
set -euo pipefail
cd "$(dirname "$0")/.."

export WORKSPACE_ENABLED="${WORKSPACE_ENABLED:-1}"
export KNOWLEDGE_ROOT="${KNOWLEDGE_ROOT:-$HOME/Developer/Knowledge}"
export CALENDAR_PROVIDER="${CALENDAR_PROVIDER:-auto}"

exec uv run python -m secure_agentic_ai.infrastructure.mcp.workspace_cli
