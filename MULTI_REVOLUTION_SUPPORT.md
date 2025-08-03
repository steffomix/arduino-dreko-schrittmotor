# Multi-Revolution Support Documentation

## Overview

The magnet loop antenna controller has been enhanced to support multiple motor revolutions for hardware configurations that require more than one complete turn of the stepper motor to cover all 80 channels.

## Changes Made

### Arduino Code Changes (`src/main.cpp`)

1. **New Global Variables:**
   - `stepsPerRevolution`: Steps per motor revolution (default: 4076)
   - `maxRevolutions`: Maximum number of revolutions allowed (default: 10)
   - `maxPosition`: Maximum position calculated as `maxRevolutions * stepsPerRevolution`
   - `minPosition`: Minimum position (always 0)

2. **Position Boundary Checking:**
   - Forward movements are checked against `maxPosition`
   - Backward movements are checked against `minPosition`
   - Channel commands validate target positions are within bounds

3. **New Serial Commands:**
   - `MAX<revolutions>` - Set maximum number of revolutions (1-20)
   - `RESET` - Reset current position to 0
   - Enhanced `P` command shows revolution and step within revolution
   - Enhanced `Q` command shows position limits

4. **Enhanced Position Reporting:**
   - Position commands now show total position, revolution number, and step within revolution
   - Example: "Position: 5000 (Revolution: 1, Step: 924)"

### GUI Changes (`gui/magnet_loop_controller.py`)

1. **New Configuration Parameters:**
   - `steps_per_revolution`: Configurable steps per revolution
   - `max_revolutions`: Maximum number of revolutions allowed
   - `max_position`: Calculated maximum position

2. **New GUI Section:**
   - "Motor Konfiguration (Mehrfach-Umdrehungen)" frame
   - Controls for steps per revolution and maximum revolutions
   - Real-time calculation of maximum position
   - Buttons to apply settings and send to Arduino

3. **Enhanced Validation:**
   - Channel movements check against maximum position limits
   - Step movements validate against position bounds
   - Informative error messages when limits would be exceeded

4. **New Methods:**
   - `apply_motor_config()`: Apply motor configuration settings
   - `reset_position()`: Reset position to zero
   - `send_motor_config_to_arduino()`: Send configuration to Arduino
   - Enhanced position validation in movement commands

## Configuration File Changes

The `antenna_config.json` file now includes:

```json
{
  "channel_41_position": 0,
  "channel_40_position": 2000,
  "current_channel": 41,
  "current_position": 810,
  "last_port": "/dev/ttyACM1",
  "last_rpm": 10,
  "steps_per_revolution": 4076,
  "max_revolutions": 5,
  "max_position": 20380
}
```

## Usage Instructions

### Initial Setup for Multi-Revolution Hardware

1. **Configure Motor Parameters:**
   - Open the GUI and locate the "Motor Konfiguration" section
   - Set "Schritte/Umdrehung" to your motor's steps per revolution (typically 4076)
   - Set "Max. Umdrehungen" to the number of revolutions your hardware requires
   - Click "Konfiguration übernehmen" to apply settings
   - Click "An Arduino senden" to send the maximum revolutions to the Arduino

2. **Calibrate Channel Positions:**
   - Follow the same calibration process as before
   - The system will automatically validate that channel positions are within the new limits
   - If a channel calculation exceeds the maximum position, you'll get a warning

3. **Reset Position if Needed:**
   - Use the "Position zurücksetzen" button to reset the motor position to 0
   - This is useful when starting calibration or if position tracking gets out of sync

### Arduino Commands

The Arduino now supports these additional commands:

- `MAX5` - Set maximum to 5 revolutions
- `MAX10` - Set maximum to 10 revolutions  
- `RESET` - Reset current position to 0
- `P` - Enhanced position reporting with revolution info
- `Q` - Enhanced status with position limits

### Position Validation

The system now prevents movements that would:
- Exceed the maximum position (max_revolutions × steps_per_revolution)
- Go below position 0
- Move to channels whose calculated positions are outside the valid range

## Backward Compatibility

- Existing single-revolution setups continue to work with default settings
- Configuration files without the new parameters will use safe defaults
- The Arduino defaults to 10 maximum revolutions if not configured

## Troubleshooting

### Common Issues:

1. **"Channel outside maximum position" errors:**
   - Increase the maximum number of revolutions
   - Verify your channel calibration positions are correct
   - Check that your hardware actually requires multiple revolutions

2. **Position gets out of sync:**
   - Use the "Position synchronisieren" button in the GUI
   - Use the Arduino `RESET` command to reset position to 0
   - Recalibrate the channel positions

3. **Configuration not taking effect:**
   - Make sure to click "Konfiguration übernehmen" in the GUI
   - Send the configuration to Arduino with "An Arduino senden"
   - Check the log output for any error messages

## Examples

### Single Revolution Setup (Legacy):
- Steps per revolution: 4076
- Max revolutions: 1
- Max position: 4076
- Channels 1-80 fit within one revolution

### Multi-Revolution Setup:
- Steps per revolution: 4076  
- Max revolutions: 5
- Max position: 20380
- Channels 1-80 spread across multiple revolutions
- More precise positioning possible

## Technical Notes

- The Arduino uses signed long integers for position tracking, supporting positions up to approximately 2 billion steps
- The GUI validates input ranges to prevent overflow or invalid configurations
- Position tracking is maintained across power cycles through the configuration file
- The system automatically calculates maximum position when revolution settings change
