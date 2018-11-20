import statistics
import time

import RPi.GPIO as GPIO
import Adafruit_ADS1x15

from api.power_supply import PowerSupply


def signnum(value):
    return int(value/abs(value)) if value != 0 else 0

class Demagnitizer():
    GAIN = 2
    TRIALS = 10

    def __init__(self, ps: PowerSupply,  hall_sensor_pin: int = 0, relay1_pin: int = 5, relay2_pin: int = 6):
        self.ps = ps

        self.hall_sensor_pin = hall_sensor_pin
        self.adc = Adafruit_ADS1x15.ADS1115()

        self.relay1_pin = relay1_pin
        self.relay2_pin = relay2_pin

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(relay1_pin, GPIO.OUT)
        GPIO.setup(relay2_pin, GPIO.OUT)

    def __del__(self):
        GPIO.cleanup()

    def get_field(self, difference=False) -> int:
        """
        Returns outlier-omitted mean readings from hall sensor
        :param difference: Set to True if differential reading required
        :return: Outlier-omitted average of trials
        """
        readings = []

        for i in range(Demagnitizer.TRIALS):
            if difference:
                readings.append(self.adc.read_adc_difference(self.hall_sensor_pin, gain=Demagnitizer.GAIN))
            else:
                readings.append(self.adc.read_adc(self.hall_sensor_pin, gain=Demagnitizer.GAIN))

        mean = statistics.mean(readings)
        deviation = statistics.stdev(readings)

        # Remove outliers in readings to account for bouncing or interference
        upper_bound = mean + deviation
        lower_bound = mean - deviation

        # Filter outliers
        filtered_readings = [reading for reading in readings if lower_bound < reading < upper_bound]

        return int(statistics.mean(filtered_readings)) if len(filtered_readings) > 0 else -1

    def get_field_average(self, trials: int) -> int:
        """
        Takes an average of the outlier-omitted field readings over a specified number of trials
        :param trials: Number of trials
        :return: Average of all trials
        """
        value = 0
        for i in range(trials):
            try:
                value += self.get_field()
            except:
                return -1
        return int(value / trials)

    def calibrate(self, trials = 20) -> int:
        """
        Gets the no-field reading from the Hall Sensor
        :param trials: Number of trials
        :return: No field reading
        """
        print('Calibrating no field condition...')
        no_field = self.get_field_average(trials)
        print('Calibration complete')

        return no_field

    def demag_current(self, no_field: int, saturation_current: float = 1.5, demag_current: float = 0.05,
                      termination_threshold: float = 0.004):
        """
        Runs the demagnetization routine using current
        :param no_field: The initial no_field value
        :param saturation_current: Current value used to saturate solenoid
        :param demag_current: Current value used to demagnetize solenoid
        :param termination_threshold: percent of no_field required acceptable as 0 field
        """
        print("No Field Value: %f" % no_field)

        GPIO.output(self.relay1_pin, GPIO.LOW)
        GPIO.output(self.relay2_pin, GPIO.HIGH)

        print('Ensuring saturation please wait.')
        self.ps.set_current(saturation_current)
        self.ps.enable_output()
        time.sleep(10)
        self.ps.disable_output()

        GPIO.output(self.relay1_pin, GPIO.LOW)
        GPIO.output(self.relay2_pin, GPIO.HIGH)

        present_field = self.get_field()
        original_sign = signnum(present_field - no_field)

        print('Present Field: %f' % present_field)
        print('Original sign: %f' % original_sign)
        self.ps.set_current(demag_current)

        overshoot = False

        for i in range(15):
            print("The 0-field value is: %d" % no_field)
            GPIO.output(self.relay2_pin, GPIO.LOW)
            time.sleep(0.1)
            self.ps.enable_output()
            time.sleep(0.3) # This allows for the delay of the ps to turn on before opening the circuit
            GPIO.output(self.relay2_pin, GPIO.HIGH)
            self.ps.disable_output()
            time.sleep(0.5) # Delay for inductance before field reading

            present_field = self.get_field()

            print('Present Field: %f' % present_field)

            if abs(present_field - no_field) > termination_threshold*no_field and signnum(present_field - no_field) != original_sign:
                overshoot = True
                break

        if overshoot:
            print('Overshoot of %d' % abs(present_field - no_field))
            self.ps.set_current(demag_current)

            for i in range(5):
                GPIO.output(self.relay1_pin, GPIO.LOW)
                GPIO.output(self.relay2_pin, GPIO.HIGH)

                self.ps.enable_output()
                self.ps.disable_output()

                GPIO.output(self.relay1_pin, GPIO.HIGH)
                time.sleep(0.5) # Delay for inductance before field reading

                present_field = self.get_field()

                if abs(present_field - no_field) > termination_threshold * no_field and signnum(
                        present_field - no_field) != original_sign:
                    break

        time.sleep(1)
        present_field = self.get_field()
        print('Final Field is: %d' % present_field)
        print('Off by: %d' % (present_field - no_field))

        self.ps.disable_output()