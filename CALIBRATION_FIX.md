# Kalibrierungs-Fix für Magnet Loop Controller

## Problem
Das Arduino verwendete hardcoded 30 Schritte pro Kanal statt der kalibrierten 25,32 Schritte. Außerdem kannte das Arduino die Kalibrierung nicht und startete immer bei Position 0.

## Lösung

### Arduino-Erweiterungen (main.cpp)
1. **Neue Kalibrierungs-Variablen:**
   - `channel41Position` - Basis-Position für Kanal 41 (niedrigste Frequenz)
   - `channel40Position` - Position für Kanal 40 (höchste Frequenz)
   - `calibrationReceived` - Flag für empfangene Kalibrierung

2. **Neue Befehle:**
   - `CAL<ch41_pos>,<ch40_pos>` - Kalibrierung senden (z.B. `CAL1000,2500`)
   - `SETPOS<position>` - Aktuelle Position setzen (z.B. `SETPOS1000`)

3. **Verbesserte Kanal-Berechnung:**
   - Verwendet kalibrierte Werte wenn verfügbar
   - Berechnet exakte Position basierend auf Frequenz-Mapping
   - Fallback zu 30 Schritten nur bei fehlender Kalibrierung

### Python-Controller-Erweiterungen (magnet_loop_controller.py)
1. **Automatische Kalibrierungs-Übertragung:**
   - Sendet Kalibrierung 3 Sekunden nach Verbindungsaufbau
   - Sendet aktuelle Position an Arduino
   - Synchronisiert Position zwischen Controller und Arduino

2. **Neue GUI-Funktion:**
   - "Kalibrierung an Arduino senden" Button
   - Verbesserte Position-Synchronisation

3. **Erweiterte Response-Verarbeitung:**
   - Erkennt Kalibrierungs-Bestätigung
   - Warnt bei Fallback-Verwendung
   - Bessere Fehlerbehandlung

## Verwendung

### Nach dem Update:
1. Arduino mit neuer Firmware flashen
2. Python-GUI starten
3. Verbindung aufbauen
4. Kalibrierung wird automatisch übertragen

### Manuelle Kalibrierung senden:
- Button "Kalibrierung an Arduino senden" verwenden
- Oder bei Verbindungsproblemen Verbindung neu aufbauen

### Arduino-Befehle (für Debugging):
```
CAL1000,2500    # Kalibrierung: CH41=1000, CH40=2500
SETPOS1000      # Position auf 1000 setzen
CH42            # Zu Kanal 42 fahren (verwendet nun kalibrierte Werte)
P               # Position abfragen
```

## Log-Ausgaben
- `✓ Arduino hat Kalibrierung empfangen` - Kalibrierung erfolgreich
- `✓ Arduino Position gesetzt: 1000` - Position synchronisiert
- `⚠ Warnung: Verwende Fallback-Berechnung` - Kalibrierung fehlt

## Vorteile
- **Exakte Kanalpositionierung:** Verwendet kalibrierten Wert von 25,32 Schritten/Kanal
- **Positionssynchronisation:** Arduino kennt die aktuelle Position
- **Automatische Übertragung:** Kalibrierung wird beim Verbinden gesendet
- **Robustheit:** Fallback-Mechanismus bei Übertragungsfehlern
