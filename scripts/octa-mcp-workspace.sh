#!/usr/bin/env bash
# Octa Workspace MCP — read-only calendar, wiki, board, review tools for Cursor (stdio).
set -euo pipefail
cd "$(dirname "$0")/.."

export WORKSPACE_ENABLED="${WORKSPACE_ENABLED:-1}"
export KNOWLEDGE_ROOT="${KNOWLEDGE_ROOT:-$HOME/Developer/Knowledge}"
export OCTA_LEDGER="${OCTA_LEDGER:-$HOME/.octa/ledger.sqlite}"
export CALENDAR_PROVIDER="${CALENDAR_PROVIDER:-auto}"
export LLM_PROVIDER="${LLM_PROVIDER:-dry}"
export RAG_BACKEND="${RAG_BACKEND:-memory}"

exec uv run python -m secure_agentic_ai.infrastructure.mcp.workspace_cli
