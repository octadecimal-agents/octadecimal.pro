#!/usr/bin/env bash
set -euo pipefail

echo "=== Secure Agentic AI Platform Demo ==="
echo ""

# 1. Verify environment
echo "[1/4] Checking environment..."
if ! command -v uv &>/dev/null; then
    echo "ERROR: uv not found. Install from https://docs.astral.sh/uv/"
    exit 1
fi
echo "  uv: $(uv --version)"
echo ""

# 2. Install dependencies
echo "[2/4] Installing dependencies..."
uv sync --quiet
echo "  Done."
echo ""

# 3. Run quality checks
echo "[3/4] Running quality checks..."
echo "  Tests: $(uv run pytest --tb=short --quiet 2>&1 | tail -1)"
echo "  Lint: $(uv run ruff check src/ tests/ --quiet && echo 'PASS')"
echo "  Types: $(uv run mypy src/ --quiet && echo 'PASS')"
echo ""

# 4. Start demo
echo "[4/4] Starting demo server..."
echo ""
echo "  Seeding demo data..."
uv run python scripts/seed_demo.py
echo ""
echo "  Starting server at http://127.0.0.1:8000"
echo ""
echo "  Open http://127.0.0.1:8000/operator/ in your browser"
echo "  Try: POST /actions with:"
echo '    curl -X POST http://127.0.0.1:8000/actions \'
echo "      -H 'Content-Type: application/json' \\"
echo "      -d '{\"actor_id\":\"agent-001\",\"actor_type\":\"agent\",\"action_type\":\"file.write\",\"description\":\"Write generated file\",\"risk_level\":\"high\"}'"
echo ""
exec uv run uvicorn src.secure_agentic_ai.adapters.api.app:app
