import time
import os
import RPi.GPIO as GPIO

# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Cobbler
PIN_CLK = 16
PIN_DO  = 26
PIN_DI  = 19
PIN_CS  = 13

def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    # set up the SPI interface pins
    GPIO.setup(PIN_DI,  GPIO.OUT)
    GPIO.setup(PIN_DO,  GPIO.IN)
    GPIO.setup(PIN_CLK, GPIO.OUT)
    GPIO.setup(PIN_CS,  GPIO.OUT)
    
def destroy():
	GPIO.cleanup()    

# read SPI data from ADC8032
def getADC(channel):
	# 1. CS LOW.
        GPIO.output(PIN_CS, True)      # clear last transmission
        GPIO.output(PIN_CS, False)     # bring CS low

	# 2. Start clock
        GPIO.output(PIN_CLK, False)  # start clock low

	# 3. Input MUX address
        for i in [1,1,channel]: # start bit + mux assignment
                 if (i == 1):
                         GPIO.output(PIN_DI, True)
                 else:
                         GPIO.output(PIN_DI, False)

                 GPIO.output(PIN_CLK, True)
                 GPIO.output(PIN_CLK, False)

        # 4. read 8 ADC bits
        ad = 0
        for i in range(8):
                GPIO.output(PIN_CLK, True)
                GPIO.output(PIN_CLK, False)
                ad <<= 1 # shift bit
                if (GPIO.input(PIN_DO)):
                        ad |= 0x1 # set first bit

        # 5. reset
        GPIO.output(PIN_CS, True)

        return ad

def loop():
    while True:
        print("ADC[0]: {}\t ADC[1]: {}".format(getADC(0), getADC(1)))
        time.sleep(1)

if __name__ == "__main__":
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        destroy()

