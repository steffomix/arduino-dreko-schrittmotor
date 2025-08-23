#!/usr/bin/env python3
"""
Test script to verify calibration functionality
"""

import sys
import os
sys.path.insert(0, '/home/melanie/Arduino/Projekte/magloop-stepmotor-2/gui')

from magnet_loop_controller import Configuration

def test_calibration():
    """Test calibration calculations"""
    config = Configuration("test_config.json")
    
    # Set test calibration data
    config.set("channel_41_position", 1000)  # CH41 at position 1000
    config.set("channel_40_position", 2975)  # CH40 at position 2975
    
    print("=== Kalibrierungs-Test ===")
    print(f"CH41 Position: {config.get('channel_41_position')}")
    print(f"CH40 Position: {config.get('channel_40_position')}")
    
    # Check calibration validity
    valid, msg = config.is_calibration_valid()
    print(f"Kalibrierung gültig: {valid} - {msg}")
    
    # Calculate steps per channel
    steps_per_channel = config.get_steps_per_channel()
    print(f"Schritte pro Kanal: {steps_per_channel:.2f}")
    
    # Expected: (2975 - 1000) / 79 = 1975 / 79 = 25.00 steps per channel
    expected_steps = (2975 - 1000) / 79
    print(f"Erwartete Schritte pro Kanal: {expected_steps:.2f}")
    
    print("\n=== Kanal-Position Tests ===")
    
    # Test some channel positions
    test_channels = [41, 42, 43, 50, 40]
    for channel in test_channels:
        position = config.calculate_channel_position(channel)
        freq_pos = config.get_channel_frequency_position(channel)
        calculated_channel = config.calculate_channel_from_position(position) if position else None
        
        print(f"Kanal {channel:2d}: Freq-Pos {freq_pos:2d}, Motor-Pos {position:7.1f}, Rück-Kanal {calculated_channel}")
    
    print("\n=== Frequenz-Reihenfolge Test ===")
    print("Erste 10 Kanäle nach Frequenz (niedrigste zuerst):")
    for i in range(10):
        channel = config.get_channel_from_frequency_position(i)
        print(f"  Freq-Pos {i:2d}: Kanal {channel}")
    
    print("\nLetzte 10 Kanäle nach Frequenz (höchste zuletzt):")
    for i in range(70, 80):
        channel = config.get_channel_from_frequency_position(i)
        print(f"  Freq-Pos {i:2d}: Kanal {channel}")
    
    # Clean up test file
    if os.path.exists("test_config.json"):
        os.remove("test_config.json")

if __name__ == "__main__":
    test_calibration()
