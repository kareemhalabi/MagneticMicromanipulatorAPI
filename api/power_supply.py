import threading
import time
from typing import Union

import serial

MIN_STEP_PERIOD = 0.1

_Num = Union[int, float]


class PowerSupply:

    def __init__(self, comm_port: str):
        self.serial_conn = serial.Serial(comm_port, baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                                         stopbits=serial.STOPBITS_TWO)

        self.serial_conn.write(b'*IDN?\n')
        print(self.serial_conn.readline().decode('ascii'))
        self.disable_output()
        self.serial_conn.write(b'VOLT:RANG HIGH\n')  # Sets to 20V mode
        self.serial_conn.write(b'APPL MAX, 0.0\n')  # Sets 20V, 0A

        self.wave = None

    def __del__(self):
        self.serial_conn.close()

    def _toggle_output(self, on: bool):
        output_str = b'ON' if on else b'OFF'

        self.serial_conn.write(b'OUTP ' + output_str + b'\n')

    def enable_output(self):
        self._toggle_output(True)

    def disable_output(self):
        self._toggle_output(False)

    def set_voltage(self, voltage: _Num):
        self.serial_conn.write(b'VOLT %f\n' % voltage)

    def set_current(self, current: _Num):
        self.serial_conn.write(b'CURR %f\n' % current)

    def set_current_step(self, current_step: _Num):
        self.serial_conn.write(b'CURR:STEP %f\n' % current_step)

    def step_current(self, up: bool):
        up_or_down = b'UP' if up else b'DOWN'
        self.serial_conn.write(b'CURR ' + up_or_down + b'\n')

    def get_error(self):
        self.serial_conn.write(b'SYST:ERR?\n')
        return self.serial_conn.readline()

    def start_square_wave(self, amplitude: _Num, period: _Num, duty_cycle: float = 0.5):

        if not (0 < duty_cycle < 1):
            raise ValueError('Duty Cycle must be between 0 and 1')

        if period < MIN_STEP_PERIOD:
            raise ValueError('Period must be at least %d seconds' % MIN_STEP_PERIOD)

        if amplitude < 0:
            raise ValueError('Amplitude must be positive')

        self.wave = _SquareWave(self, amplitude, period, duty_cycle)
        self.wave.start()

    def start_ramp_wave(self, amplitude: _Num, rise_time: _Num, steady_time: _Num, rest_time: _Num):

        if rise_time < MIN_STEP_PERIOD:
            raise ValueError('Period must be at least %d seconds' % MIN_STEP_PERIOD)

        if amplitude < 0:
            raise ValueError('Amplitude must be positive')

        self.wave = _RampWave(self, amplitude, rise_time, steady_time, rest_time)
        self.wave.start()

    def stop_wave(self):
        if self.wave is None:
            print('No wave is running')
            return

        self.wave.running = False
        del self.wave


class _SquareWave(threading.Thread):

    def __init__(self, power_supply: PowerSupply, amplitude: _Num, period: _Num, duty_cycle: float):
        self.power_supply = power_supply
        self.amplitude = amplitude

        self.power_supply.disable_output()
        self.power_supply.set_current(0)
        self.power_supply.set_current_step(amplitude)

        self.period = period
        self.duty_cycle = duty_cycle

        self.running = False

        super().__init__()

    def __del__(self):
        self.running = False

    def run(self):
        self.running = True
        self.power_supply.enable_output()
        while self.running:
            self.power_supply.step_current(up=True)
            time.sleep(self.duty_cycle * self.period)
            self.power_supply.step_current(up=False)
            time.sleep((1 - self.duty_cycle) * self.period)

        self.power_supply.disable_output()


class _RampWave(threading.Thread):

    # Total period is rise_time + steady_time + rest_time
    def __init__(self, power_supply: PowerSupply, amplitude: _Num, rise_time: _Num, steady_time: _Num, rest_time: _Num):
        self.power_supply = power_supply
        self.amplitude = amplitude

        self.num_steps = round(rise_time / MIN_STEP_PERIOD)
        self.steady_time = steady_time
        self.rest_time = rest_time

        self.power_supply.disable_output()
        self.power_supply.set_current(0)
        self.power_supply.set_current_step(amplitude / self.num_steps)

        super().__init__()

    def run(self):
        self.running = True
        self.power_supply.enable_output()
        while self.running:
            i = 0
            while i < self.num_steps:
                self.power_supply.step_current(up=True)
                time.sleep(MIN_STEP_PERIOD)
                i += 1

            time.sleep(self.steady_time)

            self.power_supply.set_current(0.0)

            time.sleep(self.rest_time)

        self.power_supply.disable_output()
