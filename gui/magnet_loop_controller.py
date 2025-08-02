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
from datetime import datetime

class MagnetLoopController:
    def __init__(self, root):
        self.root = root
        self.root.title("Magnet Loop Antenna Controller - 11m Band")
        self.root.geometry("800x600")
        
        # Serial connection variables
        self.serial_connection = None
        self.is_connected = False
        self.reading_thread = None
        self.stop_reading = False
        
        # Create GUI
        self.create_widgets()
        self.refresh_ports()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10", width=800, height=600)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
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
        
        # Control Frame
        control_frame = ttk.LabelFrame(main_frame, text="Stepper Kontrolle", padding="5")
        control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
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
        log_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Log text widget
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=70)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Clear log button
        ttk.Button(log_frame, text="Log löschen", command=self.clear_log).grid(row=1, column=0, pady=(5, 0))
        
        main_frame.rowconfigure(2, weight=1)
    
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
            except Exception as e:
                self.log(f"Lesefehler: {str(e)}")
                break
            time.sleep(0.1)
    
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
        else:
            command = f"B{steps}"
        self.send_command(command)
    
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
