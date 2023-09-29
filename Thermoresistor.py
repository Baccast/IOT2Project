# ...
# Global variables
temperature_Celsius = 0.0
temperature_threshold = 0.0
alarm_on = False  # Initialize alarm to off

# ...

def toggle_alarm():
    global alarm_on
    alarm_on = not alarm_on

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
                # Turn off the buzzer
                GPIO.output(BUZZER_PIN, GPIO.LOW)

        time.sleep(0.2)

# ...

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

    # Create a button to toggle the alarm
    alarm_button = tk.Button(root, text="Toggle Alarm", command=toggle_alarm)
    alarm_button.pack()

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
