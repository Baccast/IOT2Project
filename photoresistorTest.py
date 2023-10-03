import ADC2
import time

def main():
    ADC2.setup()

    try:
        while True:
            # Read the light sensor value
            light_value = ADC2.getADC(0)

            # Print the value to the console
            print(f"Light Sensor Value: {light_value}")

            time.sleep(1)

    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        ADC2.destroy()

if __name__ == "__main__":
    main()
