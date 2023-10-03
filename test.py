import RPi.GPIO as GPIO
import time

# GPIO pin for the LED
LED_PIN = 21  # Change this to the actual GPIO pin you are using for the LED

def main():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_PIN, GPIO.OUT)

    try:
        while True:
            print("Turning on the LED...")
            GPIO.output(LED_PIN, GPIO.HIGH)  # Turn on the LED
            time.sleep(2)  # Wait for 2 seconds

            print("Turning off the LED...")
            GPIO.output(LED_PIN, GPIO.LOW)  # Turn off the LED
            time.sleep(2)  # Wait for 2 seconds

    except KeyboardInterrupt:
        pass

    GPIO.cleanup()

if __name__ == '__main__':
    main()