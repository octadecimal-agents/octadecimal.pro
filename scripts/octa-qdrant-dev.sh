#!/usr/bin/env bash
# Start Qdrant dev instance on localhost:6335 (maps container 6333).
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is required to run Qdrant dev." >&2
  exit 1
fi

docker compose -f docker-compose.qdrant-dev.yml up -d

echo ""
echo "Qdrant dev"
echo "  REST:  http://127.0.0.1:6335"
echo "  gRPC:  http://127.0.0.1:6335:6334 (via host mapping if enabled)"
echo ""
echo "Use with Octa Workspace:"
echo "  export RAG_BACKEND=qdrant"
echo "  export QDRANT_URL=http://127.0.0.1:6335"
echo "  ./scripts/octa-mvp-up.sh"
