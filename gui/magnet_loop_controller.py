#!/usr/bin/env python3
"""
Magnet Loop Antenna Controller GUI
==================================
GUI for controlling stepper motor of a 11m band magnet loop antenna
with variable capacitor for 80 channels.

Requirements:
    pip install pyserial tkinter

Author: Generated for Arduino Stepper Control
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import serial
import serial.tools.list_ports
import threading
import time
import json
import os
from datetime import datetime

class Configuration:
    """Configuration management for the antenna controller"""
    
    def __init__(self, config_file="antenna_config.json"):
        self.config_file = config_file
        self.config = {
            "channel_41_position": 0,  # Base position offset to match Arduino behavior
            "channel_40_position": 2400,  # Highest frequency position (channel 40)
            "current_channel": 41,  # Current channel position
            "current_position": 0,  # Current motor position
            "last_port": "",  # Last used serial port
            "last_rpm": 12  # Last used RPM setting
        }
        
        # Arduino channel to frequency position mapping (CB Funk Frequenz-Reihenfolge)
        # Dies ist die Reihenfolge der Kanäle nach Frequenz (niedrigste zu höchste)
        # Index = Frequenz-Position (0 = niedrigste Frequenz, 79 = höchste Frequenz)
        # Wert = Kanal-Nummer
        self.frequency_order_channels = [
            41, 42, 43, 44, 45, 46, 47, 48, 49, 50,  # Frequenz-Positionen 0-9: Kanäle 41-50
            51, 52, 53, 54, 55, 56, 57, 58, 59, 60,  # Frequenz-Positionen 10-19: Kanäle 51-60
            61, 62, 63, 64, 65, 66, 67, 68, 69, 70,  # Frequenz-Positionen 20-29: Kanäle 61-70
            71, 72, 73, 74, 75, 76, 77, 78, 79, 80,  # Frequenz-Positionen 30-39: Kanäle 71-80
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10,          # Frequenz-Positionen 40-49: Kanäle 1-10
            11, 12, 13, 14, 15, 16, 17, 18, 19, 20,  # Frequenz-Positionen 50-59: Kanäle 11-20
            21, 22, 23, 24, 25, 26, 27, 28, 29, 30,  # Frequenz-Positionen 60-69: Kanäle 21-30
            31, 32, 33, 34, 35, 36, 37, 38, 39, 40   # Frequenz-Positionen 70-79: Kanäle 31-40
        ]
        
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
        except Exception as e:
            print(f"Error loading config: {e}")
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set configuration value"""
        self.config[key] = value
    
    def get_channel_frequency_position(self, channel):
        """Gibt die Frequenz-Position für einen Kanal zurück (0-79)"""
        try:
            return self.frequency_order_channels.index(channel)
        except ValueError:
            return None
    
    def get_channel_from_frequency_position(self, freq_pos):
        """Gibt den Kanal für eine Frequenz-Position zurück"""
        if 0 <= freq_pos < len(self.frequency_order_channels):
            return self.frequency_order_channels[freq_pos]
        return None
    
    def is_calibration_valid(self):
        """Prüft ob die Kalibrierung gültig ist"""
        ch40_pos = self.config.get("channel_40_position", -1)
        ch41_pos = self.config.get("channel_41_position", -1)
        
        # Kalibrierung muss vorliegen
        if ch40_pos < 0 or ch41_pos < 0:
            return False, "Kalibrierung fehlt: Beide Kanäle müssen kalibriert werden"
        
        # Positionen müssen in gültigen Bereichen sein
        if not (0 <= ch40_pos <= 4075) or not (0 <= ch41_pos <= 4075):
            return False, "Kalibrierung ungültig: Positionen müssen zwischen 0 und 4075 liegen"
        
        # Kanal 40 muss höher als Kanal 41 sein (niedrigere Frequenz = niedrigere Position)
        if ch40_pos < ch41_pos:
            return False, "Kalibrierung ungültig: Kanal 40 muss höher als Kanal 41 sein"
        
        return True, "Kalibrierung gültig"
    
    def get_steps_per_channel(self):
        """Berechnet Schritte pro Kanal aus der Kalibrierung"""
        valid, msg = self.is_calibration_valid()
        if not valid:
            return 30.0  # Fallback-Wert
        
        ch40_pos = self.config.get("channel_40_position", 0)
        ch41_pos = self.config.get("channel_41_position", 0)
        
        # Kanal 40 ist bei Frequenz-Position 79, Kanal 41 bei Position 0
        # Der Unterschied ist 79 Frequenz-Positionen
        frequency_positions_diff = 79  # Von Position 0 (Kanal 41) zu Position 79 (Kanal 40)
        motor_positions_diff = ch40_pos - ch41_pos
        
        return motor_positions_diff / frequency_positions_diff
    
    def calculate_channel_position(self, channel):
        """Calculate motor position for a given channel using calibration"""
        if channel < 1 or channel > 80:
            return None
        
        # Prüfe Kalibrierung
        valid, msg = self.is_calibration_valid()
        if not valid:
            return None
        
        # Finde Frequenz-Position des Kanals
        freq_pos = self.get_channel_frequency_position(channel)
        if freq_pos is None:
            return None
        
        # Berechne Position basierend auf Kalibrierung
        ch41_pos = self.config.get("channel_41_position", 0)  # Frequenz-Position 0
        steps_per_channel = self.get_steps_per_channel()
        
        # Motorposition = Basis-Position + (Frequenz-Position * Schritte pro Kanal)
        return ch41_pos + (freq_pos * steps_per_channel)
    
    def calculate_channel_from_position(self, position):
        """Calculate channel number from motor position using calibration"""
        # Prüfe Kalibrierung
        valid, msg = self.is_calibration_valid()
        if not valid:
            return 41  # Fallback zu Kanal 41
        
        # Berechne Frequenz-Position aus Motor-Position
        ch41_pos = self.config.get("channel_41_position", 0)  # Frequenz-Position 0
        steps_per_channel = self.get_steps_per_channel()
        
        if steps_per_channel <= 0:
            return 41  # Fallback
        
        # Frequenz-Position = (Motor-Position - Basis-Position) / Schritte pro Kanal
        relative_position = position - ch41_pos
        freq_pos = round(relative_position / steps_per_channel)
        
        # Begrenze auf gültigen Bereich
        freq_pos = max(0, min(79, freq_pos))
        
        # Finde Kanal für diese Frequenz-Position
        return self.get_channel_from_frequency_position(freq_pos)
    
    def get_calculated_steps_per_channel(self):
        """Get steps per channel - calculated from calibration positions for display only"""
        return self.get_steps_per_channel()

class MagnetLoopController:
    def __init__(self, root):
        self.root = root
        self.root.title("Magnet Loop Antenna Controller - 11m Band")
        self.root.geometry("900x700")
        
        # Configuration management
        self.config = Configuration()
        
        # Serial connection variables
        self.serial_connection = None
        self.is_connected = False
        self.reading_thread = None
        self.stop_reading = False
        
        # Motor status tracking
        self.motor_is_moving = False
        self.position_synced = True  # Track if position is synchronized
        
        # Create GUI
        self.create_widgets()
        self.refresh_ports()
        self.load_settings()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Main canvas with scrollbar for scrolling functionality
        self.canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and canvas
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Main frame inside the scrollable area
        main_frame = ttk.Frame(self.scrollable_frame, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.scrollable_frame.columnconfigure(0, weight=1)
        self.scrollable_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Connection Frame
        connection_frame = ttk.LabelFrame(main_frame, text="Verbindung", padding="5")
        connection_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(connection_frame, text="Port:").grid(row=0, column=0, padx=(0, 5))
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(connection_frame, textvariable=self.port_var, state="readonly", width=50)
        self.port_combo.grid(row=0, column=1, padx=(0, 5))
        
        ttk.Button(connection_frame, text="Aktualisieren", command=self.refresh_ports).grid(row=0, column=2, padx=(0, 5))
        
        self.connect_button = ttk.Button(connection_frame, text="Verbinden", command=self.toggle_connection)
        self.connect_button.grid(row=0, column=3, padx=(0, 5))
        
        self.status_label = ttk.Label(connection_frame, text="Nicht verbunden", foreground="red")
        self.status_label.grid(row=0, column=4, padx=(5, 0))
        
        # Motor status indicator
        self.motor_status_var = tk.StringVar()
        self.motor_status_label = ttk.Label(connection_frame, textvariable=self.motor_status_var, 
                                          font=("Arial", 10, "bold"), foreground="green")
        self.motor_status_label.grid(row=0, column=5, padx=(10, 0))
        self.update_motor_status_display()
        
        # Channel Control Frame
        channel_frame = ttk.LabelFrame(main_frame, text="Kanal Kontrolle (CB Linear)", padding="5")
        channel_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Current channel display
        current_channel_frame = ttk.Frame(channel_frame)
        current_channel_frame.grid(row=0, column=0, columnspan=4, pady=(0, 10))
        
        ttk.Label(current_channel_frame, text="Aktueller Kanal:").grid(row=0, column=0, padx=(0, 5))
        self.current_channel_var = tk.StringVar()
        self.current_channel_label = ttk.Label(current_channel_frame, textvariable=self.current_channel_var, 
                                             font=("Arial", 14, "bold"), foreground="blue")
        self.current_channel_label.grid(row=0, column=1, padx=(0, 20))
        
        # Position sync status
        self.sync_status_var = tk.StringVar()
        self.sync_status_label = ttk.Label(current_channel_frame, textvariable=self.sync_status_var, 
                                         foreground="green")
        self.sync_status_label.grid(row=0, column=2, padx=(20, 0))
        
        # Channel navigation buttons
        nav_frame = ttk.Frame(channel_frame)
        nav_frame.grid(row=1, column=0, columnspan=4, pady=(0, 10))
        
        ttk.Label(nav_frame, text="Kanal Navigation:").grid(row=0, column=0, columnspan=4, pady=(0, 5))
        
        # Channel down buttons
        ttk.Button(nav_frame, text="Kanal -10", command=lambda: self.change_channel(-10)).grid(row=1, column=0, padx=2)
        ttk.Button(nav_frame, text="Kanal -1", command=lambda: self.change_channel(-1)).grid(row=1, column=1, padx=2)
        
        # Direct channel entry
        ttk.Label(nav_frame, text="Gehe zu Kanal:").grid(row=1, column=2, padx=(10, 5))
        self.goto_channel_var = tk.StringVar()
        goto_entry = ttk.Entry(nav_frame, textvariable=self.goto_channel_var, width=5)
        goto_entry.grid(row=1, column=3, padx=(0, 5))
        ttk.Button(nav_frame, text="Go", command=self.goto_channel).grid(row=1, column=4, padx=(0, 10))
        
        # Channel up buttons
        ttk.Button(nav_frame, text="Kanal +1", command=lambda: self.change_channel(1)).grid(row=1, column=5, padx=2)
        ttk.Button(nav_frame, text="Kanal +10", command=lambda: self.change_channel(10)).grid(row=1, column=6, padx=2)
        
        # Calibration Frame
        cal_frame = ttk.LabelFrame(main_frame, text="Kalibrierung", padding="5")
        cal_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Channel position settings
        pos_frame = ttk.Frame(cal_frame)
        pos_frame.grid(row=0, column=0, columnspan=3, pady=(0, 5))
        
        ttk.Label(pos_frame, text="Kanal 41 Position:").grid(row=0, column=0, padx=(0, 5))
        self.ch41_pos_var = tk.StringVar()
        ch41_entry = ttk.Entry(pos_frame, textvariable=self.ch41_pos_var, width=8)
        ch41_entry.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(pos_frame, text="Kanal 40 Position:").grid(row=0, column=2, padx=(0, 5))
        self.ch40_pos_var = tk.StringVar()
        ch40_entry = ttk.Entry(pos_frame, textvariable=self.ch40_pos_var, width=8)
        ch40_entry.grid(row=0, column=3, padx=(0, 10))
        
        ttk.Label(pos_frame, text="Schritte/Kanal (berechnet):").grid(row=0, column=4, padx=(0, 5))
        self.steps_per_channel_var = tk.StringVar()
        steps_entry = ttk.Entry(pos_frame, textvariable=self.steps_per_channel_var, width=8, state="readonly")
        steps_entry.grid(row=0, column=5, padx=(0, 10))
        
        # Calibration buttons
        cal_buttons_frame = ttk.Frame(cal_frame)
        cal_buttons_frame.grid(row=1, column=0, columnspan=3, pady=(5, 0))
        
        ttk.Button(cal_buttons_frame, text="Aktuelle Position als Kanal 41 setzen", 
                  command=self.set_channel_41_position).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(cal_buttons_frame, text="Aktuelle Position als Kanal 40 setzen", 
                  command=self.set_channel_40_position).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(cal_buttons_frame, text="Kalibrierung speichern", 
                  command=self.save_calibration).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(cal_buttons_frame, text="Position synchronisieren", 
                  command=self.sync_position).grid(row=0, column=3, padx=(0, 5))
        
        # Calibration status
        cal_status_frame = ttk.Frame(cal_frame)
        cal_status_frame.grid(row=2, column=0, columnspan=3, pady=(5, 0))
        
        self.calibration_status_label = ttk.Label(cal_status_frame, text="Kalibrierung prüfen...", foreground="orange")
        self.calibration_status_label.grid(row=0, column=0)
        
        # Control Frame
        control_frame = ttk.LabelFrame(main_frame, text="Manuelle Stepper Kontrolle", padding="5")
        control_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Preset buttons frame
        preset_frame = ttk.Frame(control_frame)
        preset_frame.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        ttk.Label(preset_frame, text="Vordefinierte Schritte:").grid(row=0, column=0, columnspan=4, pady=(0, 5))
        
        # Forward buttons
        ttk.Label(preset_frame, text="Vorwärts:").grid(row=1, column=0, padx=(0, 5))
        ttk.Button(preset_frame, text="1", command=lambda: self.move_steps(1, True)).grid(row=1, column=1, padx=2)
        ttk.Button(preset_frame, text="10", command=lambda: self.move_steps(10, True)).grid(row=1, column=2, padx=2)
        ttk.Button(preset_frame, text="100", command=lambda: self.move_steps(100, True)).grid(row=1, column=3, padx=2)
        ttk.Button(preset_frame, text="1000", command=lambda: self.move_steps(1000, True)).grid(row=1, column=4, padx=2)
        
        # Backward buttons
        ttk.Label(preset_frame, text="Rückwärts:").grid(row=2, column=0, padx=(0, 5), pady=(5, 0))
        ttk.Button(preset_frame, text="1", command=lambda: self.move_steps(1, False)).grid(row=2, column=1, padx=2, pady=(5, 0))
        ttk.Button(preset_frame, text="10", command=lambda: self.move_steps(10, False)).grid(row=2, column=2, padx=2, pady=(5, 0))
        ttk.Button(preset_frame, text="100", command=lambda: self.move_steps(100, False)).grid(row=2, column=3, padx=2, pady=(5, 0))
        ttk.Button(preset_frame, text="1000", command=lambda: self.move_steps(1000, False)).grid(row=2, column=4, padx=2, pady=(5, 0))
        
        # Custom steps frame
        custom_frame = ttk.Frame(control_frame)
        custom_frame.grid(row=1, column=0, columnspan=3, pady=(10, 0))
        
        ttk.Label(custom_frame, text="Individuelle Schritte:").grid(row=0, column=0, columnspan=3, pady=(0, 5))
        
        ttk.Label(custom_frame, text="Anzahl Schritte:").grid(row=1, column=0, padx=(0, 5))
        self.custom_steps_var = tk.StringVar(value="50")
        custom_entry = ttk.Entry(custom_frame, textvariable=self.custom_steps_var, width=10)
        custom_entry.grid(row=1, column=1, padx=(0, 5))
        
        ttk.Button(custom_frame, text="Vorwärts", command=self.move_custom_forward).grid(row=1, column=2, padx=(5, 2))
        ttk.Button(custom_frame, text="Rückwärts", command=self.move_custom_backward).grid(row=1, column=3, padx=(2, 0))
        
        # Control buttons
        control_buttons_frame = ttk.Frame(control_frame)
        control_buttons_frame.grid(row=2, column=0, columnspan=3, pady=(15, 0))
        
        ttk.Button(control_buttons_frame, text="STOPP", command=self.stop_movement).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(control_buttons_frame, text="Position abfragen", command=self.get_position).grid(row=0, column=1, padx=(0, 10))
        
        # RPM control
        rpm_frame = ttk.Frame(control_frame)
        rpm_frame.grid(row=3, column=0, columnspan=3, pady=(15, 0))
        
        ttk.Label(rpm_frame, text="Geschwindigkeit (RPM):").grid(row=0, column=0, padx=(0, 5))
        self.rpm_var = tk.StringVar(value="12")
        rpm_entry = ttk.Entry(rpm_frame, textvariable=self.rpm_var, width=5)
        rpm_entry.grid(row=0, column=1, padx=(0, 5))
        ttk.Button(rpm_frame, text="Setzen", command=self.set_rpm).grid(row=0, column=2)
        
        # Status and Log Frame
        log_frame = ttk.LabelFrame(main_frame, text="Status & Log", padding="5")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Log text widget
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Clear log button
        ttk.Button(log_frame, text="Log löschen", command=self.clear_log).grid(row=1, column=0, pady=(5, 0))
        
        main_frame.rowconfigure(4, weight=1)
    
    def load_settings(self):
        """Load settings from configuration"""
        # Load calibration values into existing StringVars
        self.ch41_pos_var.set(str(self.config.get("channel_41_position", 0)))
        self.ch40_pos_var.set(str(self.config.get("channel_40_position", 2400)))
        
        # Calculate and display steps per channel (read-only)
        calculated_steps = self.config.get_calculated_steps_per_channel()
        self.steps_per_channel_var.set(f"{calculated_steps:.2f}")
        
        # Update current channel display
        self.update_channel_display()
        
        # Set last used RPM
        self.rpm_var.set(str(self.config.get("last_rpm", 12)))
        
        # Set sync status
        self.update_sync_status()
        
        # Check calibration status
        self.update_calibration_status()
        
        # Try to select last used port
        last_port = self.config.get("last_port", "")
        if last_port:
            port_values = self.port_combo['values']
            for i, port_desc in enumerate(port_values):
                if port_desc.startswith(last_port):
                    self.port_combo.current(i)
                    break
    
    def update_channel_display(self):
        """Update the current channel display"""
        current_channel = self.config.get("current_channel", 41)
        self.current_channel_var.set(f"Kanal {current_channel}")
    
    def update_sync_status(self):
        """Update the position synchronization status"""
        if self.position_synced:
            self.sync_status_var.set("Position synchronisiert")
            self.sync_status_label.config(foreground="green")
        else:
            self.sync_status_var.set("Position NICHT synchronisiert!")
            self.sync_status_label.config(foreground="red")
    
    def update_motor_status_display(self):
        """Update the motor status display"""
        if self.motor_is_moving:
            self.motor_status_var.set("🔄 Motor läuft")
            self.motor_status_label.config(foreground="orange")
        else:
            self.motor_status_var.set("⚫ Motor bereit")
            self.motor_status_label.config(foreground="green")
    
    def update_calibration_status(self):
        """Update calibration status display"""
        valid, msg = self.config.is_calibration_valid()
        if hasattr(self, 'calibration_status_label'):
            if valid:
                self.calibration_status_label.config(text=f"✓ {msg}", foreground="green")
            else:
                self.calibration_status_label.config(text=f"⚠ {msg}", foreground="red")
    
    def change_channel(self, delta):
        """Change channel by delta amount"""
        if not self.is_connected:
            messagebox.showwarning("Warnung", "Nicht mit Arduino verbunden!")
            return
        
        if self.motor_is_moving:
            messagebox.showwarning("Warnung", "Motor bewegt sich gerade. Bitte warten!")
            return
        
        # Prüfe Kalibrierung
        valid, msg = self.config.is_calibration_valid()
        if not valid:
            messagebox.showerror("Kalibrierung ungültig", f"Kanalnavigation nicht möglich:\n{msg}")
            return
        
        current_channel = self.config.get("current_channel", 41)
        new_channel = current_channel + delta
        
        # Validate channel range
        if new_channel < 1 or new_channel > 80:
            messagebox.showerror("Fehler", f"Kanal {new_channel} ist außerhalb des gültigen Bereichs (1-80)!")
            return
        
        # Send channel command to Arduino (let Arduino handle the calculations)
        self.send_command(f"CH{new_channel}")
        
        # Update current channel
        self.config.set("current_channel", new_channel)
        self.update_channel_display()
        
        # Set motor as moving
        self.motor_is_moving = True
        self.update_motor_status_display()
        
        self.log(f"Befehl gesendet: Fahre zu Kanal {new_channel}")
    
    def goto_channel(self):
        """Go directly to specified channel"""
        try:
            target_channel = int(self.goto_channel_var.get())
            
            if target_channel < 1 or target_channel > 80:
                messagebox.showerror("Fehler", "Kanal muss zwischen 1 und 80 liegen!")
                return
            
            if not self.is_connected:
                messagebox.showwarning("Warnung", "Nicht mit Arduino verbunden!")
                return
            
            if self.motor_is_moving:
                messagebox.showwarning("Warnung", "Motor bewegt sich gerade. Bitte warten!")
                return
            
            # Prüfe Kalibrierung
            valid, msg = self.config.is_calibration_valid()
            if not valid:
                messagebox.showerror("Kalibrierung ungültig", f"Kanalnavigation nicht möglich:\n{msg}")
                return
            
            # Send channel command directly to Arduino
            self.send_command(f"CH{target_channel}")
            
            # Update local tracking
            self.config.set("current_channel", target_channel)
            self.update_channel_display()
            
            # Set motor as moving
            self.motor_is_moving = True
            self.update_motor_status_display()
            
            self.log(f"Befehl gesendet: Gehe zu Kanal {target_channel}")
                
        except ValueError:
            messagebox.showerror("Fehler", "Ungültiger Kanal!")
    
    def set_channel_41_position(self):
        """Set current position as channel 41 position"""
        if not self.is_connected:
            messagebox.showwarning("Warnung", "Nicht mit Arduino verbunden!")
            return
        
        # Get current position from Arduino
        self.send_command("P")
        # Note: The actual position will be updated via serial response
        
        # For now, use the stored position
        current_pos = self.config.get("current_position", 0)
        self.config.set("channel_41_position", current_pos)
        self.ch41_pos_var.set(str(current_pos))
        
        # Update calculated steps per channel
        calculated_steps = self.config.get_calculated_steps_per_channel()
        self.steps_per_channel_var.set(f"{calculated_steps:.2f}")
        
        self.log(f"Kanal 41 Position auf {current_pos} gesetzt")
    
    def set_channel_40_position(self):
        """Set current position as channel 40 position"""
        if not self.is_connected:
            messagebox.showwarning("Warnung", "Nicht mit Arduino verbunden!")
            return
        
        # Get current position from Arduino
        self.send_command("P")
        
        # For now, use the stored position
        current_pos = self.config.get("current_position", 0)
        self.config.set("channel_40_position", current_pos)
        self.ch40_pos_var.set(str(current_pos))
        
        # Update calculated steps per channel
        calculated_steps = self.config.get_calculated_steps_per_channel()
        self.steps_per_channel_var.set(f"{calculated_steps:.2f}")
        
        self.log(f"Kanal 40 Position auf {current_pos} gesetzt")
    
    def save_calibration(self):
        """Save calibration settings"""
        try:
            # Validate and save calibration values
            ch41_pos = int(self.ch41_pos_var.get())
            ch40_pos = int(self.ch40_pos_var.get())
            
            # Validate positions are in range
            if not (0 <= ch41_pos <= 4075) or not (0 <= ch40_pos <= 4075):
                messagebox.showerror("Fehler", "Positionen müssen zwischen 0 und 4075 liegen!")
                return
            
            # Validate that CH40 < CH41 (CH40 ist niedrigere Frequenz, also niedrigere Position)
            if ch40_pos <= ch41_pos:
                messagebox.showerror("Fehler", 
                    "Kanal 40 muss eine niedrigere Position als Kanal 41 haben!\n"
                    "Kanal 40 = niedrigste Frequenz (Position sollte kleiner sein)\n"
                    "Kanal 41 = höhere Frequenz (Position sollte größer sein)")
                return
            
            # Calculate steps per channel for display
            steps_diff = ch41_pos - ch40_pos
            frequency_positions_diff = 79  # From freq pos 0 (CH41) to freq pos 79 (CH40)
            steps_per_channel = steps_diff / frequency_positions_diff
            
            # Warn if steps per channel seems unusual
            if steps_per_channel < 10 or steps_per_channel > 100:
                result = messagebox.askyesno("Warnung", 
                    f"Schritte pro Kanal: {steps_per_channel:.2f}\n"
                    "Dieser Wert scheint ungewöhnlich. Möchten Sie trotzdem speichern?")
                if not result:
                    return
            
            self.config.set("channel_41_position", ch41_pos)
            self.config.set("channel_40_position", ch40_pos)
            self.config.save_config()
            
            # Update the calculated steps per channel display
            calculated_steps = self.config.get_calculated_steps_per_channel()
            self.steps_per_channel_var.set(f"{calculated_steps:.2f}")
            
            # Update calibration status
            self.update_calibration_status()
            
            messagebox.showinfo("Info", "Kalibrierung gespeichert!")
            self.log(f"Kalibrierung gespeichert: CH41={ch41_pos}, CH40={ch40_pos}, Schritte/Kanal={calculated_steps:.2f}")
            
        except ValueError:
            messagebox.showerror("Fehler", "Ungültige Eingaben für Kalibrierung!")
    
    def sync_position(self):
        """Synchronize position with Arduino"""
        if not self.is_connected:
            messagebox.showwarning("Warnung", "Nicht mit Arduino verbunden!")
            return
        
        self.send_command("P")
        self.position_synced = True
        self.update_sync_status()
        self.log("Position mit Arduino synchronisiert")
    
    def refresh_ports(self):
        """Refresh available serial ports"""
        ports = serial.tools.list_ports.comports()
        port_list = [f"{port.device} - {port.description}" for port in ports]
        self.port_combo['values'] = port_list
        if port_list:
            self.port_combo.current(0)
    
    def toggle_connection(self):
        """Connect or disconnect from serial port"""
        if not self.is_connected:
            self.connect()
        else:
            self.disconnect()
    
    def connect(self):
        """Connect to selected serial port"""
        if not self.port_var.get():
            messagebox.showerror("Fehler", "Bitte wählen Sie einen Port aus.")
            return
        
        # Extract port name from combo box selection
        port_name = self.port_var.get().split(' - ')[0]
        
        try:
            self.serial_connection = serial.Serial(
                port=port_name,
                baudrate=9600,
                timeout=1
            )
            
            # Wait for Arduino to initialize
            time.sleep(2)
            
            self.is_connected = True
            self.connect_button.config(text="Trennen")
            self.status_label.config(text="Verbunden", foreground="green")
            
            # Start reading thread
            self.stop_reading = False
            self.reading_thread = threading.Thread(target=self.read_serial, daemon=True)
            self.reading_thread.start()
            
            self.log(f"Verbunden mit {port_name}")
            
        except Exception as e:
            messagebox.showerror("Verbindungsfehler", f"Fehler beim Verbinden: {str(e)}")
            self.log(f"Verbindungsfehler: {str(e)}")
    
    def disconnect(self):
        """Disconnect from serial port"""
        self.stop_reading = True
        if self.serial_connection:
            self.serial_connection.close()
            self.serial_connection = None
        
        self.is_connected = False
        self.connect_button.config(text="Verbinden")
        self.status_label.config(text="Nicht verbunden", foreground="red")
        self.log("Verbindung getrennt")
    
    def read_serial(self):
        """Read data from serial port in separate thread"""
        while not self.stop_reading and self.serial_connection:
            try:
                if self.serial_connection.in_waiting > 0:
                    data = self.serial_connection.readline().decode('utf-8').strip()
                    if data:
                        self.log(f"Arduino: {data}")
                        self.parse_arduino_response(data)
            except Exception as e:
                self.log(f"Lesefehler: {str(e)}")
                break
            time.sleep(0.1)
    
    def parse_arduino_response(self, response):
        """Parse Arduino response and update internal state"""
        try:
            if "Position:" in response or "Aktuelle Position:" in response:
                # Extract position from response
                parts = response.split(":")
                if len(parts) >= 2:
                    position = int(parts[1].strip())
                    self.config.set("current_position", position)
                    
                    # Update current channel based on position
                    channel = self.config.calculate_channel_from_position(position)
                    if channel:
                        self.config.set("current_channel", channel)
                        self.update_channel_display()
                        # Save configuration to keep position and channel synchronized
                        self.config.save_config()
                    
                    self.log(f"Position aktualisiert: {position} (Kanal {channel})")
            
            elif "Motor angehalten" in response or "STOPP" in response:
                self.motor_is_moving = False
                self.update_motor_status_display()
                self.log("✓ Motor gestoppt")
                
            elif "Motor fertig" in response or "Bewegung abgeschlossen" in response:
                self.motor_is_moving = False
                self.update_motor_status_display()
                self.log("✓ Motor fertig - Bewegung abgeschlossen")
                # Request position update after movement completes
                self.root.after(500, lambda: self.send_command("P"))
                
            elif "Motor startet" in response:
                self.motor_is_moving = True
                self.update_motor_status_display()
                if "Kanal" in response:
                    # Extract channel number from response
                    try:
                        parts = response.split()
                        for i, part in enumerate(parts):
                            if part == "Kanal" and i + 1 < len(parts):
                                channel = int(parts[i + 1])
                                self.config.set("current_channel", channel)
                                self.update_channel_display()
                                break
                    except (ValueError, IndexError):
                        pass
                self.log("⚡ " + response)
                
            elif "Fahre zu Kanal" in response:
                self.motor_is_moving = True
                self.update_motor_status_display()
                # Extract channel number from response
                try:
                    parts = response.split()
                    for i, part in enumerate(parts):
                        if part == "Kanal" and i + 1 < len(parts):
                            channel = int(parts[i + 1])
                            self.config.set("current_channel", channel)
                            self.update_channel_display()
                            break
                except (ValueError, IndexError):
                    pass
                self.log("➡ " + response)
                
            elif "Fahre" in response and "Schritte" in response:
                self.motor_is_moving = True
                self.update_motor_status_display()
                # Mark position as potentially out of sync for manual moves
                if "Schritte" in response and self.position_synced:
                    self.position_synced = False
                    self.update_sync_status()
                self.log("➡ " + response)
            
            elif "Bereits auf Kanal" in response:
                # Motor is not moving when already on target channel
                self.motor_is_moving = False
                self.update_motor_status_display()
                # Extract channel number
                try:
                    parts = response.split()
                    channel = int(parts[-1])
                    self.config.set("current_channel", channel)
                    self.update_channel_display()
                    self.log("✓ " + response)
                except (ValueError, IndexError):
                    self.log("✓ " + response)
                    
            elif "Motor Status:" in response:
                if "Bereit" in response:
                    self.motor_is_moving = False
                    self.update_motor_status_display()
                elif "Beschäftigt" in response:
                    self.motor_is_moving = True
                    self.update_motor_status_display()
                    
        except Exception as e:
            self.log(f"Fehler beim Verarbeiten der Arduino-Antwort: {e}")
    
    def send_command(self, command):
        """Send command to Arduino"""
        if not self.is_connected or not self.serial_connection:
            messagebox.showwarning("Warnung", "Nicht mit Arduino verbunden!")
            return False
        
        try:
            self.serial_connection.write(f"{command}\n".encode('utf-8'))
            self.log(f"Gesendet: {command}")
            return True
        except Exception as e:
            self.log(f"Sendefehler: {str(e)}")
            return False
    
    def move_steps(self, steps, forward=True):
        """Move stepper motor by specified steps"""
        if forward:
            command = f"F{steps}"
            # Update estimated position
            current_pos = self.config.get("current_position", 0)
            self.config.set("current_position", current_pos + steps)
        else:
            command = f"B{steps}"
            # Update estimated position
            current_pos = self.config.get("current_position", 0)
            self.config.set("current_position", current_pos - steps)
        
        self.send_command(command)
        self.motor_is_moving = True
        self.update_motor_status_display()
    
    def move_custom_forward(self):
        """Move forward with custom step count"""
        try:
            steps = int(self.custom_steps_var.get())
            if steps > 0:
                self.move_steps(steps, True)
            else:
                messagebox.showerror("Fehler", "Anzahl Schritte muss positiv sein!")
        except ValueError:
            messagebox.showerror("Fehler", "Ungültige Eingabe für Schritte!")
    
    def move_custom_backward(self):
        """Move backward with custom step count"""
        try:
            steps = int(self.custom_steps_var.get())
            if steps > 0:
                self.move_steps(steps, False)
            else:
                messagebox.showerror("Fehler", "Anzahl Schritte muss positiv sein!")
        except ValueError:
            messagebox.showerror("Fehler", "Ungültige Eingabe für Schritte!")
    
    def stop_movement(self):
        """Stop stepper movement"""
        self.send_command("S")
        self.motor_is_moving = False
        self.update_motor_status_display()
    
    def get_position(self):
        """Get current stepper position"""
        self.send_command("P")
    
    def set_rpm(self):
        """Set stepper RPM"""
        try:
            rpm = int(self.rpm_var.get())
            if 1 <= rpm <= 20:
                self.send_command(f"RPM{rpm}")
            else:
                messagebox.showerror("Fehler", "RPM muss zwischen 1 und 20 liegen!")
        except ValueError:
            messagebox.showerror("Fehler", "Ungültige RPM Eingabe!")
    
    def log(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        # Thread-safe GUI update
        self.root.after(0, self._update_log, log_message)
    
    def _update_log(self, message):
        """Update log text widget (must be called from main thread)"""
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)
    
    def clear_log(self):
        """Clear log text"""
        self.log_text.delete(1.0, tk.END)
    
    def on_closing(self):
        """Handle application closing"""
        # Check if motor is moving
        if self.motor_is_moving:
            result = messagebox.askyesno(
                "Warnung", 
                "Der Motor bewegt sich noch!\n\n"
                "Wenn Sie jetzt schließen, kann die aktuelle Position nicht korrekt gespeichert werden.\n"
                "Dies bedeutet, dass beim nächsten Start die Position möglicherweise nicht synchronisiert ist.\n\n"
                "Möchten Sie trotzdem schließen?\n\n"
                "Empfehlung: Warten Sie, bis der Motor gestoppt hat, oder verwenden Sie den STOPP-Button.",
                icon='warning'
            )
            if not result:
                return
            
            # Mark position as not synced for next startup
            self.position_synced = False
            self.log("WARNUNG: GUI geschlossen während Motor bewegung - Position könnte ungenau sein!")
        
        # Save current settings
        try:
            # Save current port
            if self.port_var.get():
                port_name = self.port_var.get().split(' - ')[0]
                self.config.set("last_port", port_name)
            
            # Save current RPM
            try:
                rpm = int(self.rpm_var.get())
                self.config.set("last_rpm", rpm)
            except ValueError:
                pass
            
            # Save configuration
            self.config.save_config()
            self.log("Konfiguration gespeichert")
            
        except Exception as e:
            self.log(f"Fehler beim Speichern der Konfiguration: {e}")
        
        # Disconnect and close
        if self.is_connected:
            self.disconnect()
        self.root.destroy()

def main():
    """Main function"""
    root = tk.Tk()
    app = MagnetLoopController(root)
    root.mainloop()

if __name__ == "__main__":
    main()
