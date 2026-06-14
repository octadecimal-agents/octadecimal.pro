#!/usr/bin/env bash
# Start Octa Workspace MVP on M5 (localhost:8042).
set -euo pipefail
cd "$(dirname "$0")/.."

export WORKSPACE_ENABLED=1
export KNOWLEDGE_ROOT="${KNOWLEDGE_ROOT:-$HOME/Developer/Knowledge}"
export OCTA_LEDGER="${OCTA_LEDGER:-$HOME/.octa/ledger.sqlite}"
export LLM_PROVIDER="${LLM_PROVIDER:-dry}"

mkdir -p data "$(dirname "$OCTA_LEDGER")"

echo "Syncing dependencies..."
uv sync

echo "Seeding core demo (HITL approvals)..."
uv run python scripts/seed_demo.py

echo "Seeding workspace plan..."
uv run python scripts/seed_workspace_mvp.py

echo ""
echo "Octa Workspace MVP"
echo "  UI:       http://127.0.0.1:8042/"
echo "  Operator: http://127.0.0.1:8042/operator/"
echo "  Health:   http://127.0.0.1:8042/workspace/health"
echo ""

exec uv run uvicorn secure_agentic_ai.adapters.api.app:app --host 127.0.0.1 --port 8042
