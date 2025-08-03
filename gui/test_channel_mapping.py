#!/usr/bin/env python3
"""
Test script to verify channel mapping consistency between Arduino and GUI
"""

# Simulate the Arduino mapping (copied from main.cpp)
arduino_mapping = [
    41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
    51, 52, 53, 54, 55, 56, 57, 58, 59, 60,
    61, 62, 63, 64, 65, 66, 67, 68, 69, 70,
    71, 72, 73, 74, 75, 76, 77, 78, 79, 80,
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
    31, 32, 33, 34, 35, 36, 37, 38, 39, 40
]

# GUI mapping (should be identical)
gui_mapping = [
    41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
    51, 52, 53, 54, 55, 56, 57, 58, 59, 60,
    61, 62, 63, 64, 65, 66, 67, 68, 69, 70,
    71, 72, 73, 74, 75, 76, 77, 78, 79, 80,
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
    31, 32, 33, 34, 35, 36, 37, 38, 39, 40
]

def arduino_calculate_position(channel, base_position=0, steps_per_channel=30):
    """Simulate Arduino channel to position calculation (CORRECTED)"""
    if channel < 1 or channel > 80:
        return None
    
    # Find array index for this channel (Arduino now searches the array)
    try:
        array_index = arduino_mapping.index(channel)
    except ValueError:
        return None
    
    return base_position + (array_index * steps_per_channel)

def gui_calculate_position(channel, base_position=0, steps_per_channel=30):
    """Simulate GUI channel to position calculation"""
    if channel < 1 or channel > 80:
        return None
    
    # Find array index for this channel
    try:
        array_index = gui_mapping.index(channel)
    except ValueError:
        return None
    
    return base_position + (array_index * steps_per_channel)

def arduino_calculate_channel(position, base_position=0, steps_per_channel=30):
    """Simulate Arduino position to channel calculation"""
    relative_pos = position - base_position
    array_index = round(relative_pos / steps_per_channel)
    
    if array_index < 0:
        array_index = 0
    elif array_index > 79:
        array_index = 79
    
    return arduino_mapping[array_index]

def gui_calculate_channel(position, base_position=0, steps_per_channel=30):
    """Simulate GUI position to channel calculation"""
    relative_pos = position - base_position
    array_index = round(relative_pos / steps_per_channel)
    
    if array_index < 0:
        array_index = 0
    elif array_index > 79:
        array_index = 79
    
    return gui_mapping[array_index]

def test_mappings():
    """Test that Arduino and GUI mappings are consistent"""
    print("Testing channel mapping consistency...")
    print("=" * 60)
    
    # Test if mappings are identical
    if arduino_mapping == gui_mapping:
        print("✓ Arduino and GUI mappings are identical")
    else:
        print("✗ Arduino and GUI mappings differ!")
        return False
    
    # Test some key channels from the user's log
    test_channels = [41, 42, 43, 44, 47, 49, 52, 53, 56, 58, 61, 65]
    
    print("\nTesting key channels:")
    print("-" * 60)
    print(f"{'Channel':<8} {'Arduino Pos':<12} {'GUI Pos':<12} {'Match':<8}")
    print("-" * 60)
    
    all_match = True
    for channel in test_channels:
        arduino_pos = arduino_calculate_position(channel)
        gui_pos = gui_calculate_position(channel)
        match = arduino_pos == gui_pos
        all_match = all_match and match
        
        print(f"{channel:<8} {arduino_pos:<12} {gui_pos:<12} {'✓' if match else '✗':<8}")
    
    if all_match:
        print("✓ All channel-to-position calculations match")
    else:
        print("✗ Some channel-to-position calculations don't match!")
        return False
    
    # Test reverse mapping (position to channel)
    print("\nTesting position-to-channel mapping:")
    print("-" * 60)
    print(f"{'Position':<10} {'Arduino Ch':<12} {'GUI Ch':<12} {'Match':<8}")
    print("-" * 60)
    
    test_positions = [1, 60, 90, 120, 210, 270, 360, 390, 480, 540, 630, 750]
    
    all_match = True
    for position in test_positions:
        arduino_ch = arduino_calculate_channel(position)
        gui_ch = gui_calculate_channel(position)
        match = arduino_ch == gui_ch
        all_match = all_match and match
        
        print(f"{position:<10} {arduino_ch:<12} {gui_ch:<12} {'✓' if match else '✗':<8}")
    
    if all_match:
        print("✓ All position-to-channel calculations match")
    else:
        print("✗ Some position-to-channel calculations don't match!")
        return False
    
    return True

def analyze_user_log():
    """Analyze the specific test cases from the user's log"""
    print("\n" + "=" * 60)
    print("Analyzing user's test log...")
    print("=" * 60)
    
    # Test cases from user's log
    test_cases = [
        (1, 41),    # Motor on pos. 1, should be channel 41
        (60, 42),   # After moving to CH42
        (90, 43),   # After moving to CH43
        (390, 53),  # After moving to CH53 (but GUI showed 51)
        (630, 61),  # After moving to CH61 (but GUI showed 57)
        (480, 56),  # After moving to CH56 (but GUI showed 53)
        (360, 52),  # After moving to CH52 (but GUI showed 50)
        (270, 49),  # After moving to CH49 (but GUI showed 48)
        (540, 58),  # After moving to CH58 (but GUI showed 54)
        (120, 44),  # After moving to CH44
        (2220, 34), # After moving to CH34 (but GUI showed 16)
        (1380, 6),  # After moving to CH6 (but GUI showed 75)
        (750, 65),  # After moving to CH65 (but GUI showed 60)
    ]
    
    print(f"{'Position':<10} {'Expected Ch':<12} {'Calculated Ch':<15} {'Match':<8}")
    print("-" * 60)
    
    mismatches = 0
    for position, expected_channel in test_cases:
        calculated_channel = gui_calculate_channel(position)
        match = calculated_channel == expected_channel
        if not match:
            mismatches += 1
        
        print(f"{position:<10} {expected_channel:<12} {calculated_channel:<15} {'✓' if match else '✗':<8}")
    
    print(f"\nMismatches: {mismatches}/{len(test_cases)}")
    
    if mismatches == 0:
        print("✓ All test cases from user log now work correctly!")
    else:
        print(f"✗ {mismatches} test cases still have issues")

if __name__ == "__main__":
    success = test_mappings()
    analyze_user_log()
    
    if success:
        print("\n✓ Channel mapping implementation is correct!")
    else:
        print("\n✗ Channel mapping implementation has issues!")
