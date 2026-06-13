#!/usr/bin/env bash
set -euo pipefail

echo "=== Fix HomeBrew permissions and install portaudio ==="
echo ""

# 1. Fix HomeBrew permissions
echo "[1/3] Fixing HomeBrew directory permissions..."
sudo chmod -R g+w /opt/homebrew/var/homebrew /opt/homebrew/var/log /opt/homebrew/share
sudo chmod g+w /opt/homebrew
echo "  Done."
echo ""

# 2. Install portaudio
echo "[2/3] Installing portaudio..."
HOMEBREW_NO_AUTO_UPDATE=1 brew install portaudio
echo "  Done."
echo ""

# 3. Install pyaudio in project
echo "[3/3] Installing pyaudio Python package..."
cd "$(dirname "$0")/.."
uv add pyaudio
echo "  Done."
echo ""

echo "=== All done ==="