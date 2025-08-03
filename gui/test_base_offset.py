#!/usr/bin/env python3
"""
Test the GUI logic with base position offset
"""

class TestConfiguration:
    def __init__(self):
        self.config = {
            "channel_41_position": 0,  # Base position offset
            "steps_per_channel": 30
        }
        
        # Arduino channel to position mapping
        self.channel_to_position_mapping = [
            41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
            51, 52, 53, 54, 55, 56, 57, 58, 59, 60,
            61, 62, 63, 64, 65, 66, 67, 68, 69, 70,
            71, 72, 73, 74, 75, 76, 77, 78, 79, 80,
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
            11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
            21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
            31, 32, 33, 34, 35, 36, 37, 38, 39, 40
        ]
    
    def get(self, key):
        return self.config.get(key)
    
    def calculate_channel_position(self, channel):
        if channel < 1 or channel > 80:
            return None
        
        array_value = self.channel_to_position_mapping[channel - 1]
        steps_per_channel = self.get("steps_per_channel")
        base_position = self.config.get("channel_41_position", 0)
        return base_position + (array_value * steps_per_channel)
    
    def calculate_channel_from_position(self, position):
        steps_per_channel = self.get("steps_per_channel")
        if steps_per_channel <= 0:
            return None
        
        base_position = self.config.get("channel_41_position", 0)
        relative_position = position - base_position
        array_value = round(relative_position / steps_per_channel)
        
        for channel in range(1, 81):
            if self.channel_to_position_mapping[channel - 1] == array_value:
                return channel
        
        # Find closest if exact match not found
        closest_channel = 1
        min_diff = abs(self.channel_to_position_mapping[0] - array_value)
        
        for channel in range(1, 81):
            diff = abs(self.channel_to_position_mapping[channel - 1] - array_value)
            if diff < min_diff:
                min_diff = diff
                closest_channel = channel
        
        return closest_channel

# Test the implementation
config = TestConfiguration()

print("Testing GUI with base position offset (-29):")
print("=" * 50)

# Expected results from user log
expected_results = [
    (1, 41), (60, 42), (90, 43), (390, 53), (630, 61), 
    (480, 56), (360, 52), (270, 49), (540, 58), (120, 44), 
    (2220, 34), (1380, 6), (750, 65)
]

print("Position to Channel validation:")
print("=" * 40)
all_correct = True
for position, expected_channel in expected_results:
    calculated_channel = config.calculate_channel_from_position(position)
    correct = calculated_channel == expected_channel
    all_correct = all_correct and correct
    print(f"Position {position:4d}: Expected Ch {expected_channel:2d}, Got Ch {calculated_channel:2d} {'✓' if correct else '✗'}")

print()
print("Channel to Position test:")
print("=" * 40)
for _, expected_channel in expected_results[:8]:  # Test first few
    calculated_position = config.calculate_channel_position(expected_channel)
    print(f"Channel {expected_channel:2d}: Position {calculated_position:4d}")

print()
if all_correct:
    print("✓ All position-to-channel validations passed!")
else:
    print("✗ Some position-to-channel validations failed.")

# Special test for channel 41 at position 1
ch41_pos = config.calculate_channel_position(41)
pos1_ch = config.calculate_channel_from_position(1)
print(f"\nSpecial tests:")
print(f"Channel 41 position: {ch41_pos} (should be near 1)")
print(f"Position 1 channel: {pos1_ch} (should be 41)")
