#!/usr/bin/env bash
# Start Octa Workspace MVP on M5 (localhost:8042).
set -euo pipefail
cd "$(dirname "$0")/.."

export WORKSPACE_ENABLED=1
export KNOWLEDGE_ROOT="${KNOWLEDGE_ROOT:-$HOME/Developer/Knowledge}"
export OCTA_LEDGER="${OCTA_LEDGER:-$HOME/.octa/ledger.sqlite}"
export LLM_PROVIDER="${LLM_PROVIDER:-dry}"
export RAG_BACKEND="${RAG_BACKEND:-memory}"
export QDRANT_URL="${QDRANT_URL:-http://127.0.0.1:6335}"
export QDRANT_COLLECTION="${QDRANT_COLLECTION:-knowledge_chunks_dev}"
export DEEPSEEK_MODEL="${DEEPSEEK_MODEL:-deepseek-v4-flash}"
export BWS_PROJECT_NAME="${BWS_PROJECT_NAME:-multi-agents-framework-m1}"
export BWS_DEEPSEEK_SECRET_KEY="${BWS_DEEPSEEK_SECRET_KEY:-DEEPSEEK_API_KEY}"

mkdir -p data "$(dirname "$OCTA_LEDGER")"

if [[ "${LLM_PROVIDER}" == "deepseek" && -z "${DEEPSEEK_API_KEY:-}" && -z "${BWS_ACCESS_TOKEN:-}" ]]; then
  BW_LIB="${KNOWLEDGE_ROOT}/01-Base-Point/tools/bitwarden/lib.sh"
  BW_LABEL="${DEEPSEEK_BW_LABEL:-octadecimal-infra/deepseek-api-key}"
  if [[ -f "${BW_LIB}" ]]; then
    echo "LLM_PROVIDER=deepseek — resolving API key from Bitwarden vault (${BW_LABEL})..."
    # shellcheck source=/dev/null
    DEEPSEEK_API_KEY="$(source "${BW_LIB}" && bw_load_session && bw_get_secret "${BW_LABEL}")" || true
    export DEEPSEEK_API_KEY
  fi
fi

if [[ "${RAG_BACKEND}" == "qdrant" ]]; then
  echo "RAG_BACKEND=qdrant — ensuring Qdrant dev on ${QDRANT_URL}..."
  ./scripts/octa-qdrant-dev.sh
fi

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
echo "  RAG:      ${RAG_BACKEND} (${QDRANT_URL} when qdrant)"
echo "  LLM:      ${LLM_PROVIDER} (${DEEPSEEK_MODEL} when deepseek)"
echo ""

exec uv run uvicorn secure_agentic_ai.adapters.api.app:app --host 127.0.0.1 --port 8042
