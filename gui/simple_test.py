#!/usr/bin/env python3
"""
Simple test for channel mapping
"""

# Test the mapping manually
channel_to_position_mapping = [
    41, 42, 43, 44, 45, 46, 47, 48, 49, 50,  # indices 0-9: channels 1-10 -> array values 41-50
    51, 52, 53, 54, 55, 56, 57, 58, 59, 60,  # indices 10-19: channels 11-20 -> array values 51-60
    61, 62, 63, 64, 65, 66, 67, 68, 69, 70,  # indices 20-29: channels 21-30 -> array values 61-70
    71, 72, 73, 74, 75, 76, 77, 78, 79, 80,  # indices 30-39: channels 31-40 -> array values 71-80
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10,          # indices 40-49: channels 41-50 -> array values 1-10
    11, 12, 13, 14, 15, 16, 17, 18, 19, 20,  # indices 50-59: channels 51-60 -> array values 11-20
    21, 22, 23, 24, 25, 26, 27, 28, 29, 30,  # indices 60-69: channels 61-70 -> array values 21-30
    31, 32, 33, 34, 35, 36, 37, 38, 39, 40   # indices 70-79: channels 71-80 -> array values 31-40
]

def calculate_channel_position(channel, base_pos=1000):
    """Calculate position for a channel"""
    array_value = channel_to_position_mapping[channel - 1]
    channel_41_array_value = 1
    relative_array_value = array_value - channel_41_array_value
    return base_pos + (relative_array_value * 30)

def calculate_channel_from_position(position, base_pos=1000):
    """Calculate channel from position"""
    relative_position = position - base_pos
    channel_41_array_value = 1
    relative_array_value = round(relative_position / 30)
    array_value = channel_41_array_value + relative_array_value
    
    # Find channel with this array value
    for channel in range(1, 81):
        if channel_to_position_mapping[channel - 1] == array_value:
            return channel
    return 41  # default

print("=== Channel Mapping Analysis ===")
print("Channel 41 array value:", channel_to_position_mapping[40])  # Index 40 = Channel 41
print("Channel 40 array value:", channel_to_position_mapping[39])  # Index 39 = Channel 40
print("Channel 42 array value:", channel_to_position_mapping[41])  # Index 41 = Channel 42
print()

# Test with base position 1000
base = 1000
print("=== Test with base position 1000 ===")
print(f"Channel 41 -> Position: {calculate_channel_position(41, base)}")
print(f"Channel 40 -> Position: {calculate_channel_position(40, base)}")
print(f"Channel 42 -> Position: {calculate_channel_position(42, base)}")
print()

# Test reverse calculation
test_positions = [1000, 2000, 1140, 120, 60, 360, 330]
print("=== Reverse calculation ===")
for pos in test_positions:
    channel = calculate_channel_from_position(pos, base)
    calc_back = calculate_channel_position(channel, base)
    array_val = channel_to_position_mapping[channel - 1]
    print(f"Position {pos:4d} -> Channel {channel:2d} (Array: {array_val:2d}, Back: {calc_back:4d})")
