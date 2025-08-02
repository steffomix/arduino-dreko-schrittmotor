# Magnet Loop Antenna Controller GUI

Eine grafische Benutzeroberfläche zur Steuerung des Steppmotors einer Magnet Loop Antenne für das 11m Band mit 80 Kanälen.

## Features

### Stepper Motor Kontrolle
- **Vordefinierte Schritte**: Buttons für 1, 10, 100 und 1000 Schritte vorwärts/rückwärts
- **Individuelle Schritte**: Eingabefeld für beliebige Schrittanzahl
- **Geschwindigkeitskontrolle**: RPM-Einstellung (1-20 RPM)
- **Sofortiger Stopp**: Notfall-Stopp-Button
- **Positionsabfrage**: Aktuelle Position des Motors anzeigen

### Verbindung
- **Port-Auswahl**: Automatische Erkennung verfügbarer serieller Ports
- **Port-Aktualisierung**: Refresh-Button für neue Ports
- **Verbindungsstatus**: Visueller Indikator für Verbindungsstatus

### Logging
- **Echtzeitprotokoll**: Alle Befehle und Antworten werden protokolliert
- **Zeitstempel**: Jeder Eintrag mit Zeitstempel
- **Log löschen**: Button zum Löschen des Protokolls

## Installation

### 1. Arduino-Code hochladen
Zuerst muss der Arduino-Code auf Ihren Arduino Uno R4 WiFi hochgeladen werden:

```bash
# Im Projektverzeichnis
pio run --target upload
```

### 2. GUI-Setup
```bash
cd gui
./setup.sh
```

Oder manuell:
```bash
pip3 install -r requirements.txt
```

## Verwendung

### GUI starten
```bash
cd gui
python3 magnet_loop_controller.py
```

### Verbindung herstellen
1. Arduino Uno R4 WiFi per USB verbinden
2. GUI starten
3. Korrekten Port auswählen (normalerweise `/dev/ttyACM0` oder ähnlich)
4. "Verbinden" klicken
5. Warten bis Status "Verbunden" anzeigt

### Motor steuern

#### Vordefinierte Schritte
- **Vorwärts**: Buttons 1, 10, 100, 1000 für entsprechende Schrittanzahl
- **Rückwärts**: Buttons 1, 10, 100, 1000 für entsprechende Schrittanzahl rückwärts

#### Individuelle Schritte
1. Gewünschte Schrittanzahl eingeben
2. "Vorwärts" oder "Rückwärts" Button klicken

#### Weitere Funktionen
- **STOPP**: Sofortiger Halt der Bewegung
- **Position abfragen**: Zeigt aktuelle Position im Log
- **RPM setzen**: Geschwindigkeit zwischen 1-20 RPM einstellen

## Arduino Befehle

Die GUI sendet folgende Befehle an den Arduino:

- `F<zahl>` - Vorwärts bewegen (z.B. `F100` für 100 Schritte)
- `B<zahl>` - Rückwärts bewegen (z.B. `B50` für 50 Schritte)
- `S` - Bewegung stoppen
- `P` - Position abfragen
- `RPM<zahl>` - RPM setzen (z.B. `RPM15`)

## Hardware-Anschlüsse

### Arduino Uno R4 WiFi zu ULN2003 Treiber
- Pin 8 → IN1
- Pin 9 → IN2
- Pin 10 → IN3
- Pin 11 → IN4
- GND → GND
- 5V → VCC

### ULN2003 zu 28BYJ-48 Stepper Motor
- Verbindung über das mitgelieferte Kabel

## Technische Details

### Stepper Motor
- **Typ**: 28BYJ-48 (5V)
- **Schritte pro Umdrehung**: 4096 (mit Getriebe)
- **Standard-RPM**: 12 (einstellbar 1-20)

### Serielle Kommunikation
- **Baudrate**: 9600
- **Format**: ASCII-Befehle mit Zeilenende (`\n`)

## Fehlerbehebung

### Verbindungsprobleme
- Überprüfen Sie, ob der Arduino korrekt angeschlossen ist
- Stellen Sie sicher, dass der richtige Port ausgewählt ist
- Prüfen Sie, ob andere Programme den Port verwenden
- Aktualisieren Sie die Port-Liste

### Motor bewegt sich nicht
- Überprüfen Sie die Verkabelung zwischen Arduino und ULN2003
- Prüfen Sie die Stromversorgung (5V)
- Stellen Sie sicher, dass der Arduino-Code korrekt hochgeladen wurde

### GUI-Probleme
- Stellen Sie sicher, dass alle Python-Abhängigkeiten installiert sind
- Prüfen Sie, ob Python3 und tkinter installiert sind

## Anpassungen für Ihre Antenne

Da die Schritte zwischen den Kanälen nicht linear sind, können Sie:

1. **Kalibrierung durchführen**: Nutzen Sie die individuellen Schritte zur Feinabstimmung
2. **Positionen speichern**: Notieren Sie sich die optimalen Positionen für jeden Kanal
3. **RPM anpassen**: Je nach Mechanik Ihrer Antenne die Geschwindigkeit optimieren

## Lizenz

Siehe LICENSE-Datei im Hauptverzeichnis.
