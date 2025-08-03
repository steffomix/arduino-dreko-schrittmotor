#!/usr/bin/env python3
"""
Test the updated GUI logic without steps_per_channel in config
"""

class TestConfiguration:
    def __init__(self):
        self.config = {
            "channel_41_position": 0,
            "channel_40_position": 2000,
            "current_channel": 41,
            "current_position": 810,
            "last_port": "/dev/ttyACM1", 
            "last_rpm": 10
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
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def calculate_channel_position(self, channel):
        if channel < 1 or channel > 80:
            return None
        
        array_value = self.channel_to_position_mapping[channel - 1]
        steps_per_channel = 30  # Fixed Arduino value
        base_position = self.config.get("channel_41_position", 0)
        return base_position + (array_value * steps_per_channel)
    
    def calculate_channel_from_position(self, position):
        steps_per_channel = 30  # Fixed Arduino value
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
    
    def get_calculated_steps_per_channel(self):
        """Calculate steps per channel from calibration positions for display"""
        ch41_pos = self.config.get("channel_41_position", 0)
        ch40_pos = self.config.get("channel_40_position", 2400)
        
        # Channel 40 has array value 40, Channel 41 has array value 1
        # So the difference should be (40 - 1) * 30 = 39 * 30 = 1170 steps
        actual_diff = abs(ch40_pos - ch41_pos)
        
        if actual_diff > 0:
            return actual_diff / (40 - 1)  # Divide by the channel value difference
        else:
            return 30.0  # Default Arduino value

# Test the implementation
config = TestConfiguration()

print("Testing updated configuration without steps_per_channel in config:")
print("=" * 70)

# Test the current config (from user's file)
print("Current configuration:")
for key, value in config.config.items():
    print(f"  {key}: {value}")

print(f"\nCalculated steps per channel: {config.get_calculated_steps_per_channel():.2f}")
print("(This is for display only and not saved to config)")

print("\nTesting channel calculations:")
print("=" * 40)

# Test some positions from the user's previous log
test_positions = [1, 60, 90, 270, 360, 480, 630, 750, 810]

for pos in test_positions:
    channel = config.calculate_channel_from_position(pos)
    calc_pos = config.calculate_channel_position(channel)
    print(f"Position {pos:3d} -> Channel {channel:2d} -> Position {calc_pos:3d}")

print("\nValidation: Arduino fixed logic vs calculated display:")
print("=" * 60)
print("Arduino uses fixed 30 steps per channel")
print(f"GUI display shows: {config.get_calculated_steps_per_channel():.2f} steps per channel")
print("(Based on calibration positions)")

# Check if the user's current position makes sense
current_pos = config.get("current_position")
current_channel = config.calculate_channel_from_position(current_pos)
print(f"\nCurrent position {current_pos} should be channel {current_channel}")
