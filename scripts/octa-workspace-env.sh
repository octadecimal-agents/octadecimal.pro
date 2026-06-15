#!/usr/bin/env bash
# Shared environment for Octa Workspace MVP (source from startup scripts).
# Usage: source "$(dirname "$0")/octa-workspace-env.sh"

export WORKSPACE_ENABLED=1
export KNOWLEDGE_ROOT="${KNOWLEDGE_ROOT:-$HOME/Developer/Knowledge}"
export OCTA_LEDGER="${OCTA_LEDGER:-$HOME/.octa/ledger.sqlite}"
export LLM_PROVIDER="${LLM_PROVIDER:-dry}"
export RAG_BACKEND="${RAG_BACKEND:-memory}"
export QDRANT_URL="${QDRANT_URL:-http://127.0.0.1:6335}"
export QDRANT_COLLECTION="${QDRANT_COLLECTION:-knowledge_chunks_dev}"
export WORKSPACE_HOST="${WORKSPACE_HOST:-127.0.0.1}"
export WORKSPACE_PORT="${WORKSPACE_PORT:-8042}"
export MINIMAX_MODEL="${MINIMAX_MODEL:-MiniMax-M3}"
export DEEPSEEK_MODEL="${DEEPSEEK_MODEL:-deepseek-v4-flash}"
export BWS_PROJECT_NAME="${BWS_PROJECT_NAME:-multi-agents-framework-m1}"
export BWS_MINIMAX_SECRET_KEY="${BWS_MINIMAX_SECRET_KEY:-MINIMAX_API_TOKEN}"
export BWS_DEEPSEEK_SECRET_KEY="${BWS_DEEPSEEK_SECRET_KEY:-DEEPSEEK_API_KEY}"

mkdir -p data "$(dirname "$OCTA_LEDGER")"

if [[ -z "${BWS_ACCESS_TOKEN:-}" ]]; then
  BWS_ACCESS_TOKEN="$(security find-generic-password \
    -s 'pl.octadecimal.m1-runtime.BWS_ACCESS_TOKEN' \
    -a 'm1-runtime' \
    -w 2>/dev/null)" || true
  export BWS_ACCESS_TOKEN
fi

if [[ "${LLM_PROVIDER}" == "minimax" && -z "${MINIMAX_API_TOKEN:-}" && -z "${MINIMAX_API_KEY:-}" && -z "${BWS_ACCESS_TOKEN:-}" ]]; then
  BW_LIB="${KNOWLEDGE_ROOT}/01-Base-Point/tools/bitwarden/lib.sh"
  BW_LABEL="${MINIMAX_BW_LABEL:-octadecimal-infra/minimax-api-token}"
  if [[ -f "${BW_LIB}" ]]; then
    # shellcheck source=/dev/null
    MINIMAX_API_TOKEN="$(source "${BW_LIB}" && bw_load_session && bw_get_secret "${BW_LABEL}")" || true
    export MINIMAX_API_TOKEN
  fi
fi

if [[ "${LLM_PROVIDER}" == "deepseek" && -z "${DEEPSEEK_API_KEY:-}" && -z "${BWS_ACCESS_TOKEN:-}" ]]; then
  BW_LIB="${KNOWLEDGE_ROOT}/01-Base-Point/tools/bitwarden/lib.sh"
  BW_LABEL="${DEEPSEEK_BW_LABEL:-octadecimal-infra/deepseek-api-key}"
  if [[ -f "${BW_LIB}" ]]; then
    # shellcheck source=/dev/null
    DEEPSEEK_API_KEY="$(source "${BW_LIB}" && bw_load_session && bw_get_secret "${BW_LABEL}")" || true
    export DEEPSEEK_API_KEY
  fi
fi
