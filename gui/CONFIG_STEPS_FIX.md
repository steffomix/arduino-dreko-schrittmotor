# Configuration Steps Per Channel Fix

## Changes Made

### 1. Removed `steps_per_channel` from Configuration Storage
- Removed from default config in `Configuration.__init__()`
- Removed from existing `antenna_config.json` file
- No longer saved or loaded from configuration file

### 2. Updated Channel Calculation Methods
- `calculate_channel_position()`: Now uses fixed `steps_per_channel = 30` (Arduino value)
- `calculate_channel_from_position()`: Now uses fixed `steps_per_channel = 30` (Arduino value)
- Both methods no longer read from config, ensuring consistent behavior

### 3. Updated Display Calculation
- `get_calculated_steps_per_channel()`: Now calculates from calibration positions for display only
- Formula: `actual_diff / (40 - 1)` where `actual_diff = abs(ch40_pos - ch41_pos)`
- This value is only shown in the GUI but not used for channel calculations

## Result

### Before Fix:
- `steps_per_channel` was stored in config (e.g., 40 in user's config)
- Could lead to inconsistencies between Arduino (fixed 30) and GUI calculations
- Manual entry could introduce errors

### After Fix:
- Arduino uses fixed 30 steps per channel (as defined in `cbChannelSteps = 30`)
- GUI calculations use the same fixed 30 steps per channel
- Display shows calculated value (e.g., 51.28) based on calibration positions for information only
- No configuration saving/loading of this value
- Guaranteed consistency between Arduino and GUI

### Example from User's Config:
- Current position: 810
- Calculated as Channel 67 using fixed Arduino logic
- Display shows 51.28 steps/channel (based on calibration: 2000/39 ≈ 51.28)
- But calculations always use 30 steps/channel (Arduino value)

This ensures the GUI channel display is always consistent with Arduino behavior, regardless of calibration positions.
