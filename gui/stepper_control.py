#!/usr/bin/env python3
"""
Simple GUI for controlling the Arduino stepper motor
"""

import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import threading
import time

class StepperControlGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Stepper Motor Control")
        self.root.geometry("400x300")
        
        # Serial connection
        self.serial_connection = None
        self.is_connected = False
        
        self.setup_ui()
        self.update_ports()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Serial port selection
        ttk.Label(main_frame, text="Serial Port:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(main_frame, textvariable=self.port_var, width=30)
        self.port_combo.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Refresh ports button
        ttk.Button(main_frame, text="Refresh", command=self.update_ports).grid(row=0, column=3, pady=5)
        
        # Connect/Disconnect button
        self.connect_button = ttk.Button(main_frame, text="Connect", command=self.toggle_connection)
        self.connect_button.grid(row=1, column=0, columnspan=2, pady=10)
        
        # Connection status
        self.status_var = tk.StringVar(value="Disconnected")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, foreground="red")
        self.status_label.grid(row=1, column=2, columnspan=2, pady=10)
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=20)
        
        # Main control button
        self.control_button = ttk.Button(
            main_frame, 
            text="Start Motor", 
            command=self.control_motor,
            state='disabled'
        )
        self.control_button.grid(row=3, column=0, columnspan=4, pady=20, ipadx=20, ipady=10)
        
        # Motor status
        self.motor_status_var = tk.StringVar(value="Motor: Stopped")
        ttk.Label(main_frame, textvariable=self.motor_status_var).grid(row=4, column=0, columnspan=4, pady=10)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
    def update_ports(self):
        """Update the list of available serial ports"""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports
        if ports and not self.port_var.get():
            self.port_var.set(ports[0])
    
    def toggle_connection(self):
        """Connect or disconnect from the Arduino"""
        if not self.is_connected:
            self.connect_to_arduino()
        else:
            self.disconnect_from_arduino()
    
    def connect_to_arduino(self):
        """Establish serial connection with Arduino"""
        try:
            port = self.port_var.get()
            if not port:
                messagebox.showerror("Error", "Please select a serial port")
                return
            
            self.serial_connection = serial.Serial(port, 9600, timeout=1)
            time.sleep(2)  # Wait for Arduino to reset
            
            self.is_connected = True
            self.status_var.set("Connected")
            self.status_label.configure(foreground="green")
            self.connect_button.configure(text="Disconnect")
            self.control_button.configure(state='normal')
            
        except serial.SerialException as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {str(e)}")
    
    def disconnect_from_arduino(self):
        """Close serial connection"""
        if self.serial_connection:
            self.serial_connection.close()
            self.serial_connection = None
        
        self.is_connected = False
        self.status_var.set("Disconnected")
        self.status_label.configure(foreground="red")
        self.connect_button.configure(text="Connect")
        self.control_button.configure(state='disabled')
        self.motor_status_var.set("Motor: Stopped")
    
    def control_motor(self):
        """Send command to Arduino to control the motor"""
        if not self.is_connected or not self.serial_connection:
            return
        
        try:
            # Send a simple command to the Arduino
            self.serial_connection.write(b'START\n')
            self.motor_status_var.set("Motor: Running")
            
            # You can expand this to send different commands
            # For example: STOP, SPEED:500, MOVE:1000, etc.
            
        except serial.SerialException as e:
            messagebox.showerror("Communication Error", f"Failed to send command: {str(e)}")
            self.disconnect_from_arduino()

def main():
    root = tk.Tk()
    app = StepperControlGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
