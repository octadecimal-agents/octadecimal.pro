#!/usr/bin/env bash
set -euo pipefail

echo "=== Konfiguracja routingu audio ==="
echo ""

# Sprawdz dostepnosc BlackHole
echo "[1/4] Sprawdzanie BlackHole..."
if ! python3 -c "import sounddevice; any('BlackHole' in d['name'] for d in sounddevice.query_devices())" 2>/dev/null; then
    echo "  BlackHole nie jest widoczny. Wymagany restart:"
    echo "    sudo killall coreaudiod"
    echo "  lub restart systemu."
    exit 1
fi
echo "  BlackHole wykryty."
echo ""

# Zapisz konfiguracje
echo "[2/4] Zapisuje konfiguracje audio do .env..."
cd "$(dirname "$0")/.."
uv run python run_speech.py --save-config 2>&1 | grep -v "^2026-"
echo ""

# Otworz Audio MIDI Setup
echo "[3/4] Otwieram Audio MIDI Setup - utworz Multi-Output Device..."
echo ""
echo "  Instrukcja:"
echo "  1. Kliknij + (plus) w lewym dolnym rogu"
echo "  2. Wybierz 'Create Multi-Output Device'"
echo "  3. Zaznacz: Built-in Output + BlackHole 2ch"
echo "  4. Nazwij go np. 'Speakers+Loopback'"
echo "  5. Kliknij prawym na urzadzenie -> 'Use This Device For Sound Output'"
echo "  6. W dzwiek systemowy (Control Center) wybierz to urzadzenie"
echo ""
open -a "Audio MIDI Setup"
read -p "Nacisnij Enter po skonfigurowaniu Multi-Output Device..."
echo ""

# Test
echo "[4/4] Test konfiguracji..."
echo "  Aby przetestowac, uruchom w osobnym terminalu:"
echo "    cd $(pwd)"
echo "    uv run python run_speech.py"
echo ""
echo "  Odtworz cos w Firefox/YouTube - dzwiek powinien byc"
echo "  przetwarzany zamiast glosu z mikrofonu."
echo ""
echo "Gotowe."
