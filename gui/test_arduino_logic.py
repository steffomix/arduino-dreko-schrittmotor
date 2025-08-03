#!/usr/bin/env python3
"""
Test the Arduino's original logic
"""

# Arduino mapping
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

def arduino_channel_to_position(channel, steps_per_channel=30):
    """Arduino's original logic: cbChannelToPosition[channel - 1] * cbChannelSteps"""
    if channel < 1 or channel > 80:
        return None
    
    array_value = arduino_mapping[channel - 1]
    return array_value * steps_per_channel

def arduino_position_to_channel(position, steps_per_channel=30):
    """Reverse Arduino's logic to find channel from position"""
    array_value = round(position / steps_per_channel)
    
    # Find which channel has this array value
    for channel in range(1, 81):
        if arduino_mapping[channel - 1] == array_value:
            return channel
    
    # If exact match not found, find the closest
    closest_channel = 1
    min_diff = abs(arduino_mapping[0] - array_value)
    
    for channel in range(1, 81):
        diff = abs(arduino_mapping[channel - 1] - array_value)
        if diff < min_diff:
            min_diff = diff
            closest_channel = channel
    
    return closest_channel

print("Testing Arduino's original logic:")
print("=" * 50)

# Test the specific sequence from user's log
test_sequence = [
    (1, 41),   # Starting position
    ("CH42", 42),
    ("CH43", 43),
    ("CH53", 53),
    ("CH61", 61),
    ("CH56", 56),
    ("CH52", 52),
    ("CH49", 49),
    ("CH58", 58),
    ("CH44", 44),
    ("CH34", 34),
    ("CH6", 6),
    ("CH65", 65),
]

current_pos = 1
print(f"Starting: Position {current_pos}, Channel {arduino_position_to_channel(current_pos)}")
print()

for i, (command, target_channel) in enumerate(test_sequence[1:], 1):
    target_pos = arduino_channel_to_position(target_channel)
    steps_to_move = target_pos - current_pos
    current_pos = target_pos
    final_channel = arduino_position_to_channel(current_pos)
    
    print(f"Step {i}: {command}")
    print(f"  Target position: {target_pos}")
    print(f"  Steps to move: {steps_to_move}")
    print(f"  Final position: {current_pos}")
    print(f"  Calculated channel: {final_channel}")
    print(f"  Match: {'✓' if final_channel == target_channel else '✗'}")
    print()

print("Analyzing user's actual results:")
print("=" * 50)

# From user's log - actual final positions and what channel they should display
actual_results = [
    (1, 41),     # Start
    (60, 42),    # After CH42
    (90, 43),    # After CH43  
    (390, 53),   # After CH53 (GUI showed 51)
    (630, 61),   # After CH61 (GUI showed 57)
    (480, 56),   # After CH56 (GUI showed 53)
    (360, 52),   # After CH52 (GUI showed 50)
    (270, 49),   # After CH49 (GUI showed 48)
    (540, 58),   # After CH58 (GUI showed 54)
    (120, 44),   # After CH44
    (2220, 34),  # After CH34 (GUI showed 16)
    (1380, 6),   # After CH6 (GUI showed 75)
    (750, 65),   # After CH65 (GUI showed 60)
]

for position, expected_channel in actual_results:
    calculated_channel = arduino_position_to_channel(position)
    print(f"Position {position:4d}: Expected Ch {expected_channel:2d}, Calculated Ch {calculated_channel:2d}, Match: {'✓' if calculated_channel == expected_channel else '✗'}")
