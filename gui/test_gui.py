#!/usr/bin/env python3
"""
Test script for the enhanced Magnet Loop Controller GUI
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from magnet_loop_controller import main

if __name__ == "__main__":
    print("Starting Enhanced Magnet Loop Controller GUI...")
    print("New features:")
    print("- Channel navigation (1-80)")
    print("- Calibration settings")
    print("- Configuration persistence") 
    print("- Position synchronization")
    print("- Movement status tracking")
    print("")
    main()
