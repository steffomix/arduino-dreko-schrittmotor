#!/bin/bash

# Simple script to run the stepper motor GUI

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3: sudo apt update && sudo apt install python3 python3-pip"
    exit 1
fi

# Check if pyserial is installed
if ! python3 -c "import serial" &> /dev/null; then
    echo "Installing required Python packages..."
    pip3 install --user pyserial
fi

# Navigate to the GUI directory
cd "$(dirname "$0")"

# Run the GUI
echo "Starting Stepper Motor Control GUI..."
python3 stepper_control.py
