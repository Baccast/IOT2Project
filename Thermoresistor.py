#!/usr/bin/env python
import ADC0832
import time
import math
import tkinter as tk
import threading
import RPi.GPIO as GPIO

# Constants for the thermistor characteristics
R0 = 10000  # Resistance at a known temperature (in ohms)
T0 = 25     # Known temperature in Celsius (adjust as needed)
B = 3950    # Beta coefficient of the thermistor (adjust as needed)

# Global variables
temperature_Celsius = 0.0
temperature_threshold = 0.0

# GPIO pin for the buzzer
BUZZER_PIN = 23

# Potentiometer calibration values
# These values should be adjusted based on your potentiometer's characteristics
pot_min_value = 30   # Minimum ADC reading when potentiometer is at -50°C
pot_max_value = 225  # Maximum ADC reading when potentiometer is at 50°C

def init():
    ADC0832.setup()
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUZZER_PIN, GPIO.OUT)
    GPIO.output(BUZZER_PIN, GPIO.LOW)

def map_potentiometer_to_temperature(pot_value):
    # Map the potentiometer value to the desired temperature range
    temperature_C = -50 + (pot_value - pot_min_value) / (pot_max_value - pot_min_value) * 100
    return temperature_C

def temperature_from_resistance(Rt):
    try:
        # Calculate temperature in Celsius using the Steinhart-Hart equation
        inv_T = 1.0 / (T0 + 273.15) + (1.0 / B) * math.log(Rt / R0)
        temperature_C = 1.0 / inv_T - 273.15
        return temperature_C
    except ValueError:
        # Handle the case where math.log() receives an invalid argument
        return None

def update_temperature_and_threshold():
    global temperature_Celsius, temperature_threshold

    while True:
        # Read temperature and potentiometer values from ADC channels
        res_temp = ADC0832.getADC(0)  # Temperature sensor connected to channel 0
        res_pot = ADC0832.getADC(1)   # Potentiometer connected to channel 1

        Vr_temp = 3.3 * float(res_temp) / 255
        Vr_pot = 3.3 * float(res_pot) / 255

        Rt_temp = 10000 * Vr_temp / (3.3 - Vr_temp)
        
        # Calculate temperature in Celsius
        temperature_C = temperature_from_resistance(Rt_temp)
        
        if temperature_C is not None:
            temperature_F = (temperature_C * 9/5) + 32  # Convert to Fahrenheit

            # Update the global temperature variable
            temperature_Celsius = temperature_C

            # Map potentiometer value to temperature
            temperature_threshold = map_potentiometer_to_temperature(res_pot)

            # Ensure the threshold doesn't exceed 50°C
            if temperature_threshold > 50:
                temperature_threshold = 50

            # Update the GUI labels
            temperature_label.config(text=f'Temperature (Celsius): {temperature_C:.2f}°C\nTemperature (Fahrenheit): {temperature_F:.2f}°F')
            threshold_label.config(text=f'Temperature Threshold: {temperature_threshold:.2f}°C')

            # Check if temperature exceeds the threshold
            if temperature_C > temperature_threshold:
                # Turn on the buzzer
                GPIO.output(BUZZER_PIN, GPIO.HIGH)
            else:
                # Turn off the buzzer
                GPIO.output(BUZZER_PIN, GPIO.LOW)

        time.sleep(0.2)

def main():
    init()

    # Create a Tkinter window
    root = tk.Tk()
    root.title("Thermistor Temperature Monitor")

    # Create labels to display temperature and threshold
    global temperature_label, threshold_label
    temperature_label = tk.Label(root, text="", font=("Helvetica", 16))
    temperature_label.pack(padx=20, pady=10)

    threshold_label = tk.Label(root, text="", font=("Helvetica", 16))
    threshold_label.pack(padx=20, pady=10)

    # Create a button to exit the application
    exit_button = tk.Button(root, text="Exit", command=root.quit)
    exit_button.pack()

    # Start the temperature update thread
    update_thread = threading.Thread(target=update_temperature_and_threshold)
    update_thread.daemon = True
    update_thread.start()

    root.mainloop()

if __name__ == '__main__':
    main()
