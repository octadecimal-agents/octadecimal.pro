#!/usr/bin/env bash
set -euo pipefail

# E2E: Overlay screenshot test
# Starts the pipeline briefly and captures the overlay

echo "=== E2E: Overlay screenshot test ==="

SCREENSHOT="/tmp/pipecat-overlay-test.png"
TIMEOUT=6

# Kill any leftover processes
pkill -f "run_speech.py" 2>/dev/null || true

echo "[1/3] Starting speech pipeline in background..."
cd "$(dirname "$0")/../.."
uv run python3 run_speech.py &
PID=$!
echo "  PID: $PID"

# Wait for pipeline to initialize
echo "[2/3] Waiting ${TIMEOUT}s for overlay to render..."
sleep "$TIMEOUT"

# Take screenshot
echo "[3/3] Capturing screenshot..."
screencapture -x "$SCREENSHOT"
SIZE=$(stat -f%z "$SCREENSHOT" 2>/dev/null || stat -c%s "$SCREENSHOT" 2>/dev/null)

# Cleanup
kill "$PID" 2>/dev/null || true
wait "$PID" 2>/dev/null || true

# Validate
if [ ! -f "$SCREENSHOT" ]; then
    echo "  ERROR: Screenshot not created"
    exit 1
fi
if [ "$SIZE" -lt 10000 ]; then
    echo "  ERROR: Screenshot too small (${SIZE} bytes)"
    exit 1
fi
echo "  -> $SCREENSHOT ($SIZE bytes)"
rm -f "$SCREENSHOT"

echo ""
echo "=== PASS: Overlay screenshot test ==="
