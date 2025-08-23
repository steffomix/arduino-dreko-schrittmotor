#!/usr/bin/env python3
"""
Test für korrigierte Channel-Mapping Logik mit korrekten CB-Funk Frequenzen
"""

# CB Funk Frequenz-Reihenfolge (von niedrigster zu höchster Frequenz)
# Basierend auf den tatsächlichen CB-Funk Frequenzen:
# Kanal 41 = 26.565 MHz (niedrigste Frequenz)
# Kanal 40 = 27.405 MHz (höchste Frequenz)
frequency_order_channels = [
    41, 42, 43, 44, 45, 46, 47, 48, 49, 50,  # Frequenz-Positionen 0-9
    51, 52, 53, 54, 55, 56, 57, 58, 59, 60,  # Frequenz-Positionen 10-19
    61, 62, 63, 64, 65, 66, 67, 68, 69, 70,  # Frequenz-Positionen 20-29
    71, 72, 73, 74, 75, 76, 77, 78, 79, 80,  # Frequenz-Positionen 30-39
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10,          # Frequenz-Positionen 40-49
    11, 12, 13, 14, 15, 16, 17, 18, 19, 20,  # Frequenz-Positionen 50-59
    21, 22, 23, 24, 25, 26, 27, 28, 29, 30,  # Frequenz-Positionen 60-69
    31, 32, 33, 34, 35, 36, 37, 38, 39, 40   # Frequenz-Positionen 70-79
]

def get_frequency_position(channel):
    """Frequenz-Position für einen Kanal"""
    try:
        return frequency_order_channels.index(channel)
    except ValueError:
        return None

def get_channel_from_frequency_position(freq_pos):
    """Kanal für eine Frequenz-Position"""
    if 0 <= freq_pos < len(frequency_order_channels):
        return frequency_order_channels[freq_pos]
    return None

def calculate_channel_position(channel, ch41_pos, ch40_pos):
    """Berechne Motor-Position für einen Kanal"""
    freq_pos = get_frequency_position(channel)
    if freq_pos is None:
        return None
    
    # Schritte pro Kanal aus Kalibrierung
    # CH40 (höchste Freq.) > CH41 (niedrigste Freq.)
    steps_per_channel = (ch40_pos - ch41_pos) / 79  # 79 Frequenz-Positionen zwischen CH41 und CH40
    
    return ch41_pos + (freq_pos * steps_per_channel)

def calculate_channel_from_position(position, ch41_pos, ch40_pos):
    """Berechne Kanal aus Motor-Position"""
    steps_per_channel = (ch40_pos - ch41_pos) / 79
    relative_position = position - ch41_pos
    freq_pos = round(relative_position / steps_per_channel)
    freq_pos = max(0, min(79, freq_pos))  # Begrenzen
    return get_channel_from_frequency_position(freq_pos)

# Test mit korrigierter Kalibrierung: CH41=1000 (niedrig), CH40=3000 (hoch)
print("=== Korrigierte CB-Funk Kalibrierung Test ===")
ch41_pos = 1000  # Kanal 41 bei Position 1000 (niedrigste Frequenz)
ch40_pos = 3000  # Kanal 40 bei Position 3000 (höchste Frequenz)
steps_per_channel = (ch40_pos - ch41_pos) / 79

print(f"Kanal 41 (26.565 MHz) Position: {ch41_pos} (niedrigste Freq.)")
print(f"Kanal 40 (27.405 MHz) Position: {ch40_pos} (höchste Freq.)")
print(f"Schritte pro Kanal: {steps_per_channel:.2f}")
print()

print("=== Frequenz-Positionen ===")
print(f"Kanal 41 (26.565 MHz) -> Frequenz-Position: {get_frequency_position(41)}")
print(f"Kanal 40 (27.405 MHz) -> Frequenz-Position: {get_frequency_position(40)}")
print(f"Kanal 42 (26.575 MHz) -> Frequenz-Position: {get_frequency_position(42)}")
print(f"Kanal  1 (26.965 MHz) -> Frequenz-Position: {get_frequency_position(1)}")
print()

print("=== Channel -> Position ===")
test_channels = [41, 42, 50, 80, 1, 10, 40]
for channel in test_channels:
    pos = calculate_channel_position(channel, ch41_pos, ch40_pos)
    freq_pos = get_frequency_position(channel)
    print(f"Kanal {channel:2d} -> Position {pos:7.1f} (Freq-Pos: {freq_pos:2d})")

print()
print("=== Position -> Channel (Log-Simulation) ===")
log_positions = [1000, 1500, 2000, 2500, 3000]
for position in log_positions:
    channel = calculate_channel_from_position(position, ch41_pos, ch40_pos)
    calc_back = calculate_channel_position(channel, ch41_pos, ch40_pos)
    freq_pos = get_frequency_position(channel)
    print(f"Position {position:4d} -> Kanal {channel:2d} (Freq-Pos: {freq_pos:2d}, Zurück: {calc_back:7.1f})")

print()
print("=== Erwartete Ergebnisse ===")
print("Position 1000 -> Kanal 41 (niedrigste Frequenz)")
print("Position 3000 -> Kanal 40 (höchste Frequenz)")
print("Dazwischen: logische Verteilung nach Frequenz-Reihenfolge")
