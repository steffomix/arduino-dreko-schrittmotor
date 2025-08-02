#!/bin/bash

# Setup script for Magnet Loop Antenna Controller GUI

echo "=== Magnet Loop Antenna Controller Setup ==="
echo ""

# Check if Python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python3 ist nicht installiert. Bitte installieren Sie Python3 zuerst."
    exit 1
fi

echo "Python3 gefunden: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 ist nicht installiert. Bitte installieren Sie pip3 zuerst."
    exit 1
fi

echo "pip3 gefunden"

# Install required packages
echo ""
echo "Installiere Python-Abhängigkeiten..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Setup erfolgreich abgeschlossen!"
    echo ""
    echo "Um die GUI zu starten, führen Sie aus:"
    echo "  python3 magnet_loop_controller.py"
    echo ""
    echo "Stellen Sie sicher, dass:"
    echo "  1. Ihr Arduino Uno R4 WiFi mit dem Computer verbunden ist"
    echo "  2. Der Arduino-Code hochgeladen wurde"
    echo "  3. Die serielle Verbindung verfügbar ist"
else
    echo ""
    echo "✗ Fehler beim Installieren der Abhängigkeiten"
    exit 1
fi
