#!/usr/bin/env bash
# Isolated FastAPI server for Playwright E2E (port 18042).
set -euo pipefail
cd "$(dirname "$0")/.."

E2E_ROOT="${PWD}/e2e/.data"
KNOWLEDGE="${E2E_ROOT}/knowledge"
LEDGER="${E2E_ROOT}/ledger.sqlite"
DB_PATH="${PWD}/data/e2e-playwright.db"

CAL_FIXTURE="${E2E_ROOT}/calendar-fixture.json"
mkdir -p data "${E2E_ROOT}" "${KNOWLEDGE}/01-Base-Point/pro/servers/pc-ubuntu"
cat > "${CAL_FIXTURE}" <<'JSON'
[{"time": "09:00", "title": "E2E standup", "calendar": "Praca"}]
JSON
cat > "${KNOWLEDGE}/01-Base-Point/pro/servers/pc-ubuntu/Backup.md" <<'MD'
# Backup

Automatyczny backup stacku HYDRA na pc-ubuntu. Qdrant snapshot retention 30 dni.
MD

export WORKSPACE_ENABLED=1
export LLM_PROVIDER=dry
export CALENDAR_PROVIDER=fixture
export RAG_BACKEND=memory
export DATABASE_URL="sqlite+aiosqlite:///${DB_PATH}"
export OCTA_LEDGER="${LEDGER}"
export KNOWLEDGE_ROOT="${KNOWLEDGE}"
export OCTA_STATE_DIR="${E2E_ROOT}/.octa"
export OCTA_CALENDAR_FIXTURE="${CAL_FIXTURE}"

rm -f "${DB_PATH}" "${LEDGER}"

uv run python scripts/seed_demo.py
uv run python scripts/seed_workspace_mvp.py

exec uv run uvicorn secure_agentic_ai.adapters.api.app:app --host 127.0.0.1 --port 18042
