#!/usr/bin/env python
import ADC0832
import ADC2
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
alarm_on = False  # Initialize alarm to off

# GPIO pin for the buzzer
BUZZER_PIN = 23

# Define the potentiometer reading range
POT_MIN = 0    # Minimum ADC value for the potentiometer
POT_MAX = 255  # Maximum ADC value for the potentiometer

def init():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    
    # set up the SPI interface pins
    GPIO.setup(PIN_DI, GPIO.OUT)
    GPIO.setup(PIN_DO, GPIO.IN)
    GPIO.setup(PIN_CLK, GPIO.OUT)
    GPIO.setup(PIN_CS, GPIO.OUT)

    # Ensure that PIN_CS is initially set to high
    GPIO.output(PIN_CS, True)

def map_value(value, from_min, from_max, to_min, to_max):
    # Map 'value' from the range [from_min, from_max] to [to_min, to_max]
    return (value - from_min) * (to_max - to_min) / (from_max - from_min) + to_min

def temperature_from_resistance(Rt):
    try:
        # Calculate temperature in Celsius using the Steinhart-Hart equation
        inv_T = 1.0 / (T0 + 273.15) + (1.0 / B) * math.log(Rt / R0)
        temperature_C = 1.0 / inv_T - 273.15
        return temperature_C
    except ValueError:
        # Handle the case where math.log() receives an invalid argument
        return None

def set_alarm_on():
    global alarm_on
    alarm_on = True

def set_alarm_off():
    global alarm_on
    alarm_on = False

def update_temperature_and_threshold():
    global temperature_Celsius, temperature_threshold, alarm_on

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

            # Map potentiometer value to temperature threshold
            temperature_threshold = map_value(res_pot, POT_MIN, POT_MAX, 50, -50)  # Inverted mapping

            # Ensure the threshold doesn't exceed the specified range
            temperature_threshold = max(-50, min(50, temperature_threshold))

            # Update the GUI labels
            temperature_label.config(text=f'Temperature (Celsius): {temperature_C:.2f}°C\nTemperature (Fahrenheit): {temperature_F:.2f}°F')
            threshold_label.config(text=f'Temperature Threshold: {temperature_threshold:.2f}°C')

            # Check if temperature exceeds the threshold and alarm is on
            if alarm_on and temperature_C > temperature_threshold:
                # Turn on the buzzer
                GPIO.output(BUZZER_PIN, GPIO.HIGH)
            else:
                # Turn off the buzzer and update alarm status label
                GPIO.output(BUZZER_PIN, GPIO.LOW)
                alarm_status_label.config(text="Alarm Status: Off", fg="red")

            # Update alarm status label when alarm is on
            if alarm_on:
                alarm_status_label.config(text="Alarm Status: On", fg="green")

        time.sleep(0.2)

def update_light_status():
    global light_status_label

    while True:
        res_light = ADC2.getADC(0)  # Photoresistor connected to channel 0

        # Check the light level and update the label
        if res_light < 128:
            light_status = "Light"
            label_color = "green"
        else:
            light_status = "Dark"
            label_color = "red"

        # Update the GUI label with light status and color
        light_status_label.config(text=f'Light Status: {light_status}', fg=label_color)

        time.sleep(0.2)

def cleanup():
    # Turn off the buzzer
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    # Clean up GPIO
    GPIO.cleanup()

def main():
    init()

    # Create a Tkinter window
    root = tk.Tk()
    root.title("Thermistor and Photoresistor Monitor")

    # Create labels to display temperature, threshold, and alarm status
    global temperature_label, threshold_label, alarm_status_label, light_status_label
    temperature_label = tk.Label(root, text="", font=("Helvetica", 16))
    temperature_label.pack(padx=20, pady=10)

    threshold_label = tk.Label(root, text="", font=("Helvetica", 16))
    threshold_label.pack(padx=20, pady=10)

    alarm_status_label = tk.Label(root, text="Alarm Status: Off", font=("Helvetica", 16))
    alarm_status_label.pack(padx=20, pady=10)
    alarm_status_label.configure(fg="red")  # Initialize as red

    # Create a label to display light status
    light_status_label = tk.Label(root, text="", font=("Helvetica", 16))
    light_status_label.pack(padx=20, pady=10)

    # Create "On" and "Off" buttons for the alarm
    alarm_on_button = tk.Button(root, text="Alarm On", command=set_alarm_on)
    alarm_on_button.pack()

    alarm_off_button = tk.Button(root, text="Alarm Off", command=set_alarm_off)
    alarm_off_button.pack()

    # Create a button to exit the application
    exit_button = tk.Button(root, text="Exit", command=lambda: [root.quit(), cleanup()])  # Add cleanup on exit
    exit_button.pack()

    # Start the temperature update thread
    update_thread = threading.Thread(target=update_temperature_and_threshold)
    update_thread.daemon = True
    update_thread.start()

    # Start the light status update thread
    light_thread = threading.Thread(target=update_light_status)
    light_thread.daemon = True
    light_thread.start()

    root.protocol("WM_DELETE_WINDOW", lambda: [root.quit(), cleanup()])  # Add cleanup on GUI close

    root.mainloop()

if __name__ == '__main__':
    main()
