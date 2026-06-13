#!/usr/bin/env bash
set -euo pipefail

# Pipecat Translator — E2E Test Runner
# Usage: ./tests/run_all.sh [--unit-only] [--e2e-only] [--skip-e2e]

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

UNIT_ONLY=false
E2E_ONLY=false
SKIP_E2E=false
VERBOSE=false

for arg in "$@"; do
    case "$arg" in
        --unit-only) UNIT_ONLY=true ;;
        --e2e-only) E2E_ONLY=true ;;
        --skip-e2e) SKIP_E2E=true ;;
        --verbose|-v) VERBOSE=true ;;
        *) echo "Unknown option: $arg"; exit 1 ;;
    esac
done

PASS=0
FAIL=0

run_test() {
    local name="$1"
    local cmd="$2"
    echo ""
    echo "━━━ $name ━━━"
    if eval "$cmd" 2>&1; then
        echo "  ✓ PASS"
        PASS=$((PASS + 1))
    else
        echo "  ✗ FAIL"
        FAIL=$((FAIL + 1))
    fi
}

export PYTHONPATH="${ROOT}/src:${PYTHONPATH:-}"
source .venv/bin/activate

echo "╔══════════════════════════════════════════╗"
echo "║  Pipecat Translator — E2E Test Suite    ║"
echo "╚══════════════════════════════════════════╝"

# ── Unit tests ──
if ! $E2E_ONLY; then
    run_test "Unit: Config" "python3 -m pytest tests/unit/test_config.py -v --tb=short ${VERBOSE:+--log-cli-level=DEBUG}"
    run_test "Unit: RAG" "python3 -m pytest tests/unit/test_rag.py -v --tb=short ${VERBOSE:+--log-cli-level=DEBUG}"
fi

# ── Integration tests ──
if ! $E2E_ONLY; then
    run_test "Integration: PoC" "python3 -m pytest tests/integration/test_poc.py -v --tb=short ${VERBOSE:+--log-cli-level=DEBUG}"
    run_test "Integration: Pipeline" "python3 -m pytest tests/integration/test_pipeline.py -v --tb=short ${VERBOSE:+--log-cli-level=DEBUG}"
fi

# ── E2E tests (macOS-native) ──
if ! $UNIT_ONLY && ! $SKIP_E2E; then
    run_test "E2E: Audio pipeline" "bash tests/e2e/test_audio_pipeline.sh"
    run_test "E2E: RAG search" "bash tests/e2e/test_rag_search.sh"
    # Overlay test is optional — requires display
    if [ -n "${DISPLAY:-}" ] || [ "$(uname)" = "Darwin" ]; then
        run_test "E2E: Overlay screenshot" "bash tests/e2e/test_overlay.sh"
    else
        echo "  ↷ SKIP (no display available)"
    fi
fi

# ── Summary ──
echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  Results: $PASS passed, $FAIL failed"
echo "╚══════════════════════════════════════════╝"

exit $FAIL
