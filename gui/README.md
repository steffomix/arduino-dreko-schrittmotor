# Stepper Motor GUI Control

This GUI provides a simple interface to control your Arduino stepper motor from your Linux computer.

## Features

- Serial port selection and connection management
- Simple "Start Motor" button
- Real-time connection status
- Expandable for additional motor controls

## Requirements

- Python 3
- pyserial library (`pip3 install pyserial`)
- Arduino connected via USB

## Setup

1. **Upload the Arduino Code:**
   - Use PlatformIO to upload the modified `main.cpp` to your Arduino
   - The Arduino will now listen for serial commands

2. **Install Python Dependencies:**
   ```bash
   pip3 install --user pyserial
   ```

3. **Run the GUI:**
   ```bash
   ./run_gui.sh
   ```
   
   Or directly:
   ```bash
   python3 stepper_control.py
   ```

## Usage

1. **Connect Arduino:**
   - Plug in your Arduino via USB
   - Select the correct serial port from the dropdown (usually `/dev/ttyUSB0` or `/dev/ttyACM0`)
   - Click "Connect"

2. **Control Motor:**
   - Once connected, the "Start Motor" button becomes available
   - Click it to start the motor movement
   - The motor will run continuously as programmed

## Available Serial Commands

The Arduino now accepts these commands via serial:

- `START` - Start motor movement
- `STOP` - Stop motor movement  
- `SPEED:<value>` - Set motor speed (1-1000)
- `MOVE:<steps>` - Move specific number of steps

## Expanding the GUI

You can easily add more buttons and controls by:

1. Adding new UI elements in the `setup_ui()` method
2. Creating corresponding command functions
3. Adding new serial commands in the Arduino code

## Troubleshooting

- **Permission denied on serial port:** Add your user to the dialout group:
  ```bash
  sudo usermod -a -G dialout $USER
  ```
  Then log out and back in.

- **Port not found:** Make sure the Arduino is connected and drivers are installed
- **Connection fails:** Try a different baud rate or check cable connections
