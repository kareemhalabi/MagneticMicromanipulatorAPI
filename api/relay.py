import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)


class Relay:
    _relays_in_use = 0

    def __init__(self, pin_number):
        self.pin_number = pin_number
        GPIO.setup(self.pin_number, GPIO.OUT)
        Relay._relays_in_use += 1

    def __del__(self):
        Relay._relays_in_use -= 1

        if Relay._relays_in_use == 0:
            GPIO.cleanup()

    def vcc(self):
        GPIO.output(self.pin_number, GPIO.LOW)

    def gnd(self):
        GPIO.output(self.pin_number, GPIO.HIGH)
