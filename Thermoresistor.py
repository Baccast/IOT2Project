#!/usr/bin/env python
import ADC0832
import time
import math
import tkinter as tk
import threading  # Import the threading module

# Constants for the thermistor characteristics
R0 = 10000  # Resistance at a known temperature (in ohms)
T0 = 25     # Known temperature in Celsius (adjust as needed)
B = 3950    # Beta coefficient of the thermistor (adjust as needed)

# Global variable to store temperature in Celsius
temperature_Celsius = 0.0

def init():
    ADC0832.setup()

def temperature_from_resistance(Rt):
    # Calculate temperature in Celsius using the Steinhart-Hart equation
    inv_T = 1.0 / (T0 + 273.15) + (1.0 / B) * math.log(Rt / R0)
    temperature_C = 1.0 / inv_T - 273.15
    return temperature_C

def update_temperature():
    global temperature_Celsius

    while True:
        res = ADC0832.getADC(0)
        Vr = 3.3 * float(res) / 255
        Rt = 10000 * Vr / (3.3 - Vr)
        
        temperature_C = temperature_from_resistance(Rt)
        temperature_F = (temperature_C * 9/5) + 32  # Convert to Fahrenheit

        # Update the global temperature variable
        temperature_Celsius = temperature_C

        # Update the GUI label text
        temperature_label.config(text=f'Temperature (Celsius): {temperature_C:.2f}°C\nTemperature (Fahrenheit): {temperature_F:.2f}°F')

        time.sleep(0.2)

def main():
    init()

    # Create a Tkinter window
    root = tk.Tk()
    root.title("Thermistor Temperature Monitor")

    # Create a label to display temperature
    global temperature_label
    temperature_label = tk.Label(root, text="", font=("Helvetica", 16))
    temperature_label.pack(padx=20, pady=20)

    # Create a button to exit the application
    exit_button = tk.Button(root, text="Exit", command=root.quit)
    exit_button.pack()

    # Start the temperature update thread
    update_thread = threading.Thread(target=update_temperature)
    update_thread.daemon = True  # Allow the thread to exit when the main program exits
    update_thread.start()

    root.mainloop()

if __name__ == '__main__':
    main()