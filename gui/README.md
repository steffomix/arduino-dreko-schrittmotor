# Magnet Loop Antenna Controller GUI

Enhanced GUI for controlling stepper motor of a 11m band magnet loop antenna with variable capacitor for 80 CB channels.

## New Features (Enhanced Version)

### Channel Navigation
- **Direct Channel Control**: Navigate directly to any CB channel (1-80)
- **Channel Up/Down**: Move by 1 or 10 channels with dedicated buttons
- **Current Channel Display**: Shows the current channel position prominently
- **Channel History**: Channels follow the CB band layout (41-80, then 1-40)

### Calibration & Configuration
- **Position Calibration**: Set reference positions for channels 41 (lowest frequency) and 40 (highest frequency)
- **Steps per Channel**: Configure the motor steps between adjacent channels
- **Persistent Settings**: All settings are automatically saved to `antenna_config.json`
- **Position Synchronization**: Sync GUI position with actual Arduino position

### Enhanced Safety Features
- **Motor Status Tracking**: Real-time monitoring of motor movement
- **Position Sync Warning**: Alerts when position might be out of sync
- **Safe Shutdown**: Warns user when closing GUI while motor is moving
- **Movement Queue**: Commands are queued when motor is busy

### Configuration File Structure
The configuration is stored in `antenna_config.json`:
```json
{
  "channel_41_position": 0,      // Motor position for channel 41 (lowest freq)
  "channel_40_position": 2370,   // Motor position for channel 40 (highest freq)
  "steps_per_channel": 30,       // Steps between adjacent channels
  "current_channel": 41,         // Last known channel position
  "current_position": 0,         // Last known motor position
  "last_port": "/dev/ttyUSB0",   // Last used serial port
  "last_rpm": 12                 // Last used RPM setting
}
```

## Installation & Setup

### Requirements
```bash
pip install pyserial tkinter
```

### First Time Calibration
1. **Connect to Arduino** using the connection panel
2. **Manual Positioning**: Use the manual stepper controls to position the capacitor
3. **Set Channel 41**: Move to the lowest frequency position and click "Aktuelle Position als Kanal 41 setzen"
4. **Set Channel 40**: Move to the highest frequency position and click "Aktuelle Position als Kanal 40 setzen"
5. **Calculate Steps**: The steps per channel will be calculated automatically, or enter manually
6. **Save Calibration**: Click "Kalibrierung speichern" to store the settings

### Normal Operation
1. **Connect** to the Arduino
2. **Sync Position**: Click "Position synchronisieren" to sync with Arduino
3. **Navigate Channels**: Use the channel navigation buttons or direct channel entry
4. **Monitor Status**: Watch the position sync status and motor activity

## Arduino Commands

### Basic Movement
- `F<steps>` - Move forward (clockwise) by steps
- `B<steps>` - Move backward (counter-clockwise) by steps
- `S` - Stop current movement
- `P` - Get current position
- `RPM<value>` - Set RPM (6-24)
- `Q` - Get queue status

### Channel Commands (New)
- `CH<channel>` - Go directly to specified channel (1-80)
  - Example: `CH41` moves to channel 41
  - Example: `CH1` moves to channel 1

## GUI Layout

### Connection Panel
- Serial port selection and connection status
- Port refresh and connect/disconnect buttons

### Channel Control Panel
- Current channel display with sync status
- Channel navigation buttons (-10, -1, +1, +10)
- Direct channel entry and "Go" button

### Calibration Panel
- Position settings for channels 41 and 40
- Steps per channel configuration
- Calibration save and position sync buttons

### Manual Stepper Control Panel
- Preset step buttons (1, 10, 100, 1000 steps)
- Custom step entry with forward/backward buttons
- Stop button and position query
- RPM control

### Status & Log Panel
- Real-time logging of all activities
- Arduino communication display
- Clear log functionality

## Safety Features

### Position Synchronization
- The GUI tracks motor position and current channel
- When position might be out of sync, warnings are displayed
- Use "Position synchronisieren" to resync with Arduino

### Safe Application Closure
- If motor is moving when closing the GUI, a warning is displayed
- User can choose to wait or close anyway
- Position accuracy is preserved when possible

### Movement Safety
- Channel navigation is disabled when motor is busy
- Commands are queued when motor is moving
- Real-time status updates prevent conflicting commands

## Troubleshooting

### Position Out of Sync
If the position becomes out of sync:
1. Use manual controls to verify actual position
2. Query position with "Position abfragen"
3. Use "Position synchronisieren" to resync
4. Re-calibrate if necessary

### Motor Not Responding
1. Check serial connection
2. Verify correct port selection
3. Check Arduino power and connections
4. Use "STOPP" button to clear any stuck commands

### Channel Navigation Issues
1. Ensure calibration is properly set
2. Verify channel 41 and 40 positions are correct
3. Check steps per channel calculation
4. Re-run calibration procedure if needed

## Files
- `magnet_loop_controller.py` - Main GUI application
- `antenna_config.json` - Configuration file (auto-created)
- `antenna_config.json.example` - Example configuration
- `test_gui.py` - Test script to launch GUI
- `requirements.txt` - Python dependencies
- `setup.sh` - Setup script for Linux

## Running the GUI
```bash
python3 magnet_loop_controller.py
```

Or use the test script:
```bash
python3 test_gui.py
```

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
