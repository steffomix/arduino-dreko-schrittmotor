#!/usr/bin/env python3
"""
Test the updated GUI configuration logic
"""

# Simulate the GUI Configuration class
class TestConfiguration:
    def __init__(self):
        self.config = {
            "steps_per_channel": 30
        }
        
        # Arduino channel to position mapping (same as in Arduino code)
        self.channel_to_position_mapping = [
            41, 42, 43, 44, 45, 46, 47, 48, 49, 50,  # indices 0-9: channels 41-50
            51, 52, 53, 54, 55, 56, 57, 58, 59, 60,  # indices 10-19: channels 51-60
            61, 62, 63, 64, 65, 66, 67, 68, 69, 70,  # indices 20-29: channels 61-70
            71, 72, 73, 74, 75, 76, 77, 78, 79, 80,  # indices 30-39: channels 71-80
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10,          # indices 40-49: channels 1-10
            11, 12, 13, 14, 15, 16, 17, 18, 19, 20,  # indices 50-59: channels 11-20
            21, 22, 23, 24, 25, 26, 27, 28, 29, 30,  # indices 60-69: channels 21-30
            31, 32, 33, 34, 35, 36, 37, 38, 39, 40   # indices 70-79: channels 31-40
        ]
    
    def get(self, key):
        return self.config.get(key)
    
    def calculate_channel_position(self, channel):
        """Calculate motor position for a given channel using Arduino's original logic"""
        if channel < 1 or channel > 80:
            return None
        
        # Arduino logic: cbChannelToPosition[channel - 1] * cbChannelSteps
        # This uses the VALUE at array index (channel-1), not the index itself
        array_value = self.channel_to_position_mapping[channel - 1]
        steps_per_channel = self.get("steps_per_channel")
        
        return array_value * steps_per_channel
    
    def calculate_channel_from_position(self, position):
        """Calculate channel number from motor position using Arduino's original logic"""
        steps_per_channel = self.get("steps_per_channel")
        if steps_per_channel <= 0:
            return None
        
        # Reverse the Arduino calculation: position = array_value * steps_per_channel
        # So array_value = position / steps_per_channel
        array_value = round(position / steps_per_channel)
        
        # Find which channel has this array value
        # Look for array_value in the mapping array and return the corresponding channel
        for channel in range(1, 81):  # channels 1-80
            if self.channel_to_position_mapping[channel - 1] == array_value:
                return channel
        
        # If exact match not found, find the closest
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

print("Testing GUI's updated logic:")
print("=" * 50)

# Test channel to position
test_channels = [41, 42, 43, 53, 61, 56, 52, 49, 58, 44, 34, 6, 65]
print('Channel to Position:')
for ch in test_channels:
    pos = config.calculate_channel_position(ch)
    print(f'  Channel {ch:2d} -> Position {pos:4d}')

print()

# Test position to channel
test_positions = [1, 60, 90, 390, 630, 480, 360, 270, 540, 120, 2220, 1380, 750]
print('Position to Channel:')
for pos in test_positions:
    ch = config.calculate_channel_from_position(pos)
    print(f'  Position {pos:4d} -> Channel {ch:2d}')

print()

# Compare with expected results from user log
expected_results = [
    (1, 41), (60, 42), (90, 43), (390, 53), (630, 61), 
    (480, 56), (360, 52), (270, 49), (540, 58), (120, 44), 
    (2220, 34), (1380, 6), (750, 65)
]

print("Validation against user's log:")
print("=" * 50)
all_correct = True
for position, expected_channel in expected_results:
    calculated_channel = config.calculate_channel_from_position(position)
    correct = calculated_channel == expected_channel
    all_correct = all_correct and correct
    print(f"Position {position:4d}: Expected Ch {expected_channel:2d}, Got Ch {calculated_channel:2d} {'✓' if correct else '✗'}")

print()
if all_correct:
    print("✓ All validations passed! GUI should now display correct channels.")
else:
    print("✗ Some validations failed.")
