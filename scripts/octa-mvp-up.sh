#!/usr/bin/env bash
# Start Octa Workspace MVP on M5 (localhost:8042) — interactive foreground.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "${SCRIPT_DIR}/.."

# shellcheck source=scripts/octa-workspace-env.sh
source "${SCRIPT_DIR}/octa-workspace-env.sh"

if [[ "${RAG_BACKEND}" == "qdrant" ]]; then
  echo "RAG_BACKEND=qdrant — ensuring Qdrant dev on ${QDRANT_URL}..."
  ./scripts/octa-qdrant-dev.sh
fi

echo ""
echo "Octa Workspace MVP"
echo "  UI:       http://127.0.0.1:${WORKSPACE_PORT}/"
echo "  Operator: http://127.0.0.1:${WORKSPACE_PORT}/operator/"
echo "  Health:   http://127.0.0.1:${WORKSPACE_PORT}/workspace/health"
echo "  RAG:      ${RAG_BACKEND} (${QDRANT_URL} when qdrant)"
case "${LLM_PROVIDER}" in
  minimax) echo "  LLM:      minimax (${MINIMAX_MODEL})" ;;
  deepseek) echo "  LLM:      deepseek (${DEEPSEEK_MODEL})" ;;
  *) echo "  LLM:      ${LLM_PROVIDER}" ;;
esac
echo ""
echo "Tip: always-on dev → ./scripts/install-workspace-api-launchd.sh"
echo "     Runbook → docs/runbooks/workspace-daily-dev.md"
echo ""

exec ./scripts/octa-workspace-api-dev.sh --foreground
