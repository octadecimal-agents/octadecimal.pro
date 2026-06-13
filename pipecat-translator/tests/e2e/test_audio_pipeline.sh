#!/usr/bin/env bash
set -euo pipefail

# E2E: Audio pipeline test
# Uses macOS `say` to generate test audio files in WAV format
# Required flags: --file-format=WAVE --data-format=LEI16@16000

SAY_FMT="--file-format=WAVE --data-format=LEI16@16000"

echo "=== E2E: Audio pipeline (say-generated WAV validation) ==="

OUT_DIR="${1:-/tmp/pipecat-e2e}"
mkdir -p "$OUT_DIR"

# 1. Generate PL audio
echo "[1/3] Generating Polish audio..."
say -v Zosia $SAY_FMT -o "$OUT_DIR/test_pl.wav" "Dzień dobry, jak się masz?"
PL_SIZE=$(stat -f%z "$OUT_DIR/test_pl.wav" 2>/dev/null || stat -c%s "$OUT_DIR/test_pl.wav" 2>/dev/null)
echo "  -> $OUT_DIR/test_pl.wav ($PL_SIZE bytes)"

# 2. Generate EN audio
echo "[2/3] Generating English audio..."
say -v Samantha $SAY_FMT -o "$OUT_DIR/test_en.wav" "Hello, how are you?"
EN_SIZE=$(stat -f%z "$OUT_DIR/test_en.wav" 2>/dev/null || stat -c%s "$OUT_DIR/test_en.wav" 2>/dev/null)
echo "  -> $OUT_DIR/test_en.wav ($EN_SIZE bytes)"

# 3. Validate WAV files
echo "[3/3] Validating WAV files..."
python3 -c "
import sys, wave, struct
errors = []
for f in ['$OUT_DIR/test_pl.wav', '$OUT_DIR/test_en.wav']:
    try:
        w = wave.open(f, 'rb')
        frames = w.getnframes()
        rate = w.getframerate()
        ch = w.getnchannels()
        dur = frames / rate
        print(f'  {f}: {ch}ch, {rate}Hz, {dur:.1f}s, {frames} frames')
        w.close()
    except Exception as e:
        errors.append(f'{f}: {e}')
if errors:
    for e in errors:
        print(f'  ERROR: {e}', file=sys.stderr)
    sys.exit(1)
"

# 4. Cleanup
rm -rf "$OUT_DIR"

echo ""
echo "=== PASS: Audio pipeline test ==="
