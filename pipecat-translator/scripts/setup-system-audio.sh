#!/usr/bin/env bash
set -euo pipefail

echo "=== System Audio Loopback Setup ==="
echo ""
echo "Krok 1: Instalacja BlackHole (wirtualne urzadzenie audio)"
echo "  brew install blackhole-2ch"
echo "  (wymaga hasla sudo - zostanie poproszony)"
echo ""
brew install blackhole-2ch

echo ""
echo "Krok 2: Otworz Audio MIDI Setup i utworz Multi-Output Device"
echo "  1. Uruchom: open -a 'Audio MIDI Setup'"
echo "  2. Kliknij + (plus) w lewym dolnym rogu"
echo "  3. Wybierz 'Create Multi-Output Device'"
echo "  4. Zaznacz: Built-in Output + BlackHole 2ch"
echo "  5. Nazwij go np. 'Speakers+Loopback'"
echo "  6. Kliknij prawym na urzadzenie -> 'Use This Device For Sound Output'"
echo ""
open -a "Audio MIDI Setup"

echo ""
echo "Krok 3: Wybierz urzadzenie wejsciowe"
echo "  Uruchom ponizsze aby zobaczyc liste:"
echo "  python3 -c \"import sounddevice; print(sounddevice.query_devices())\""
echo ""
echo "  Szukaj 'BlackHole 2ch' na liscie input devices."
echo "  Jego indeks (np. 3) podaj jako --input-device do skryptu."
echo ""

# List devices
echo "Aktualne urzadzenia audio:"
python3 -c "
import sounddevice
devices = sounddevice.query_devices()
for i, d in enumerate(devices):
    marker = ''
    if 'BlackHole' in d['name']:
        marker = ' <<< BLACKHOLE'
    print(f'  [{i}] {d[\"name\"]} (in:{d[\"max_input_channels\"]} out:{d[\"max_output_channels\"]}){marker}')
print()
print('Aby uzyc BlackHole jako wejscia:')
print('  uv run python run_speech.py --input-device <indeks>')
" 2>&1

echo ""
echo "Gotowe."
