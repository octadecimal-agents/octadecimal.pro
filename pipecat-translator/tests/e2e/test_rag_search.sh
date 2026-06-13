#!/usr/bin/env bash
set -euo pipefail

# E2E: RAG semantic search test
# Seedes Qdrant with phrases and validates search results

echo "=== E2E: RAG search test ==="

cd "$(dirname "$0")/../.."

echo "[1/3] Running seed_rag.py..."
OUTPUT=$(uv run python3 scripts/seed_rag.py 2>&1)

if ! echo "$OUTPUT" | grep -q "Zaindeksowano 31 fraz"; then
    echo "  ERROR: Seed failed"
    echo "$OUTPUT"
    exit 1
fi
echo "  -> 31 phrases indexed"

echo "[2/3] Verifying search results..."
if ! echo "$OUTPUT" | grep -q "Potrzebujemy więcej czasu"; then
    echo "  ERROR: Expected phrase not found in search results"
    echo "$OUTPUT"
    exit 1
fi
echo "  -> Semantic search returned expected results"

echo "[3/3] Verifying topics..."
if ! echo "$OUTPUT" | grep -q "negocjacje\|terminy"; then
    echo "  ERROR: Expected topics not found"
    echo "$OUTPUT"
    exit 1
fi
echo "  -> Topics present in results"

echo ""
echo "=== PASS: RAG search test ==="
