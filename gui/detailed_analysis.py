#!/usr/bin/env python3
"""
Detailed analysis of the channel mapping issue
"""

# The mapping from Arduino code
arduino_mapping = [
    41, 42, 43, 44, 45, 46, 47, 48, 49, 50,  # indices 0-9
    51, 52, 53, 54, 55, 56, 57, 58, 59, 60,  # indices 10-19
    61, 62, 63, 64, 65, 66, 67, 68, 69, 70,  # indices 20-29
    71, 72, 73, 74, 75, 76, 77, 78, 79, 80,  # indices 30-39
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10,          # indices 40-49
    11, 12, 13, 14, 15, 16, 17, 18, 19, 20,  # indices 50-59
    21, 22, 23, 24, 25, 26, 27, 28, 29, 30,  # indices 60-69
    31, 32, 33, 34, 35, 36, 37, 38, 39, 40   # indices 70-79
]

def position_to_channel(position, base_position=0, steps_per_channel=30):
    """Convert position to channel using the mapping"""
    relative_pos = position - base_position
    array_index = round(relative_pos / steps_per_channel)
    
    if array_index < 0:
        array_index = 0
    elif array_index > 79:
        array_index = 79
    
    return arduino_mapping[array_index]

def channel_to_position(channel, base_position=0, steps_per_channel=30):
    """Convert channel to position using the mapping"""
    try:
        array_index = arduino_mapping.index(channel)
        return base_position + (array_index * steps_per_channel)
    except ValueError:
        return None

print("Channel to Position Mapping (first few channels):")
print("=" * 50)
for channel in [41, 42, 43, 44, 45, 46]:
    pos = channel_to_position(channel)
    print(f"Channel {channel:2d} -> Position {pos:3d} (array index {arduino_mapping.index(channel):2d})")

print("\nPosition to Channel Mapping (from user log):")
print("=" * 50)

# User's test cases from the log
user_positions = [1, 60, 90, 120, 210, 270, 360, 390, 480, 540, 630, 750, 1380, 2220]

for pos in user_positions:
    channel = position_to_channel(pos)
    expected_pos = channel_to_position(channel)
    print(f"Position {pos:4d} -> Channel {channel:2d} (should be at position {expected_pos:4d})")

print("\nAnalyzing specific movements from user log:")
print("=" * 60)

# Simulate the test sequence
current_pos = 1
print(f"Starting position: {current_pos}, Channel: {position_to_channel(current_pos)}")

movements = [
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
    ("CH61", 61),
    ("CH47", 47),
    ("CH36", 36)
]

for command, target_channel in movements:
    target_pos = channel_to_position(target_channel)
    steps_to_move = target_pos - current_pos
    current_pos = target_pos
    actual_channel = position_to_channel(current_pos)
    
    print(f"{command}: Target pos {target_pos:4d}, Steps: {steps_to_move:5d}, Final channel: {actual_channel:2d}")
