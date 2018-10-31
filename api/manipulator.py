from enum import Enum
from typing import Tuple, Union, Sequence

import serial

_USTEPS_PER_UM_ = 25


class Mode(Enum):
    ABSOLUTE_MODE = b'a'
    RELATIVE_MODE = b'b'


class Resolution(Enum):
    LOW = 0  # 10 uSteps/step
    HIGH = 1  # 50 uSteps/step


_Num = Union[int, float]


class Maipulator:

    def __init__(self, comm_port: str):

        self.serial_conn = serial.Serial(comm_port, baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                                         stopbits=serial.STOPBITS_ONE)

    def __del__(self):
        self.serial_conn.close()

    def get_current_position(self):
        """
        Get the micromanipulator position
        :return: A tuple of floats (x,y,z) of the position in um accurate to 0.04 um
        """
        self.serial_conn.write(b'c\r')

        # returns 'xxxxyyyyzzzzCR' in uSteps
        position_bytes = self.serial_conn.read(13)

        x = int.from_bytes(position_bytes[0:4], byteorder='little', signed=True)
        y = int.from_bytes(position_bytes[4:8], byteorder='little', signed=True)
        z = int.from_bytes(position_bytes[8:12], byteorder='little', signed=True)

        return float(x / _USTEPS_PER_UM_), float(y / _USTEPS_PER_UM_), float(z / _USTEPS_PER_UM_)

    def go_to_position(self, x: _Num, y: _Num, z: _Num):
        """
        Direct the micromanipulator to a position within an accuracy of 0.04 um

        :param x: X coordinate in um
        :param y: Y coordinate in um
        :param z: Z coordinate in um
        """

        x_bytes = int(x * _USTEPS_PER_UM_).to_bytes(4, byteorder='little', signed=True)
        y_bytes = int(y * _USTEPS_PER_UM_).to_bytes(4, byteorder='little', signed=True)
        z_bytes = int(z * _USTEPS_PER_UM_).to_bytes(4, byteorder='little', signed=True)

        self.serial_conn.write(b'm' + x_bytes + y_bytes + z_bytes + b'\r')

        # Wait for response
        self.serial_conn.read()

    def send_and_execute_moves(self, moves: Sequence[Tuple[_Num, _Num, _Num]], program_num: int = 1):
        """
        Sends and executes a sequence of moves on the manipulator. (Max 99 moves at a time)

        :param moves: List of (x, y, z) coordinates in um
        :param program_num: Optional program number between 1 and 10
        """

        if len(moves) > 99:
            raise ValueError('Maximum number of moves exceed. Limit is 99')

        if not (1 <= program_num <= 10):
            raise ValueError('Program number must be between 1 and 10')

        # Header information:
        # Command is 'd' followed by the program number followed by the number of moves
        byte_str = b'd' + program_num.to_bytes(1, byteorder='little', signed=False) \
                   + len(moves).to_bytes(1, byteorder='little', signed=False)

        for move in moves:
            x_bytes = int(move[0] * _USTEPS_PER_UM_).to_bytes(4, byteorder='little', signed=True)
            y_bytes = int(move[1] * _USTEPS_PER_UM_).to_bytes(4, byteorder='little', signed=True)
            z_bytes = int(move[2] * _USTEPS_PER_UM_).to_bytes(4, byteorder='little', signed=True)
            byte_str += x_bytes + y_bytes + z_bytes

        byte_str += b'\r'

        # Send program
        self.serial_conn.write(byte_str)

        # Wait for confirmation
        self.serial_conn.read()

        # Execute program (Command 'k')
        self.serial_conn.write(b'k' + program_num.to_bytes(1, byteorder='little', signed=False) + b'\r')

        # Wait for completion
        self.serial_conn.read()

    def set_velocity(self, velocity: _Num, resolution: Resolution):
        """
        Set the velocity of the manipulator. Two resolutions are available:

        HIGH_RESOLUTION allows for increments of 0.4um/second with max velocity of 1310 um/s

        LOW_RESOLUTION allows for increments of 2um/second with max velocity of 6500 um/s(recommended maximum 3000 um/s)

        :param velocity: velocity value in um/second
        :param resolution: Resolution either HIGH_RESOLUTION (0.4um/second) or LOW_RESOLUTION (2um/second)
        """

        if velocity <= 0:
            raise ValueError('Velocity must be positive')

        if resolution == Resolution.HIGH:
            steps = int((velocity * _USTEPS_PER_UM_) / 50)
        elif resolution == Resolution.LOW:
            steps = int((velocity * _USTEPS_PER_UM_) / 10)
        else:
            raise ValueError('Use either HIGH_RESOLUTION or LOW_RESOLUTION')

        steps = (resolution.value << 15) | steps

        self.serial_conn.write(b'V' + steps.to_bytes(2, 'little') + b'\r')

        # Wait for response
        self.serial_conn.read()

    def set_origin(self):
        """
        Sets the origin of the manipulator
        """
        self.serial_conn.write(b'o\r')

        # Wait for response
        self.serial_conn.read()

    def refresh_display(self):
        """
        Refreshes the display on the manipulator
        """
        self.serial_conn.write(b'n\r')

        # Wait for response
        self.serial_conn.read()

    def set_mode(self, mode: Mode):
        """
        Sets the mode of the manipulator
        :param mode: options are ABSOLUTE or RELATIVE
        """

        self.serial_conn.write(mode.value + b'\r')

        # Wait for response
        self.serial_conn.read()

    def interrupt(self):
        """
        Interrupts the manipulator
        """
        self.serial_conn.write(hex(3))

        # Wait for response
        self.serial_conn.read()

    def continue_operation(self):
        """
        Resumes an operation on the manipulator
        """
        self.serial_conn.write(b'e\r')

        # Wait for response
        self.serial_conn.read()

    def reset(self):
        """
        Resets the manipulator. No value is returned from the manipulator
        """
        self.serial_conn.write(b'r\r')

    def get_status(self):
        """
        Returns a dict containing all status information from the mainpulator

        :return: Dict of all status information
        """
        self.serial_conn.write(b's\r')

        status_bytes = self.serial_conn.read(33)

        flag_byte = status_bytes[0]
        flag_2_byte = status_bytes[15]

        return {
            'FLAGS': {
                'SETUP': flag_byte & 0b00001111,
                'ROE_DIR': 'Negative' if (flag_byte & (1 << 4)) == (1 << 4) else 'Positive',
                'REL_ABS_F': 'Absolute' if (flag_byte & (1 << 5)) == (1 << 5) else 'Relative',
                'MODE_F': 'Continuous' if (flag_byte & (1 << 6)) == (1 << 6) else 'Pulse',
                'STORE_F': 'Stored' if (flag_byte & (1 << 7)) == (1 << 7) else 'Erased'
            },
            'UDIRX': status_bytes[1],
            'UDIRY': status_bytes[2],
            'UDIRZ': status_bytes[3],
            'ROE_VARI': int.from_bytes(status_bytes[4:6], byteorder='little'),
            'UOFFSET': int.from_bytes(status_bytes[6:8], byteorder='little'),
            'URANGE': int.from_bytes(status_bytes[8:10], byteorder='little'),
            'PULSE': int.from_bytes(status_bytes[10:12], byteorder='little'),
            'USPEED': int.from_bytes(status_bytes[12:14], byteorder='little'),
            'INDEVICE': status_bytes[14],
            'FLAGS_2': {
                'LOOP_MODE': 'Loop' if (flag_2_byte & (1 << 0)) == (1 << 0) else 'Execute Once',
                'LEARN_MODE': 'Learning' if (flag_2_byte & (1 << 1)) == (1 << 1) else 'Not Learning',
                'STEP_MODE': '50 usteps/step' if (flag_2_byte & (1 << 2)) == (1 << 2) else '10 usteps/step',
                'JOYSTICK_SIDE': 'Enabled' if (flag_2_byte & (1 << 3)) == (1 << 3) else 'Disabled',  # SW2_MODE
                'ENABLE_JOYSTICK': 'Enabled' if (flag_2_byte & (1 << 4)) == (1 << 4) else 'Keypad',  # SW1_MODE
                'ENABLE_ROE_SWITCH': 'Enabled' if (flag_2_byte & (1 << 5)) == (1 << 5) else 'Disabled',  # SW3_MODE
                '4_AND_5_SWITCHES': 'Enabled' if (flag_2_byte & (1 << 6)) == (1 << 6) else 'Disabled',  # SW4_MODE
                'REVERSE_IT': 'Reversed' if (flag_2_byte & (1 << 7)) == (1 << 7) else 'Normal Sequence'
            },
            'JUMPSPD': int.from_bytes(status_bytes[16:18], byteorder='little'),
            'HIGHSPD': int.from_bytes(status_bytes[18:20], byteorder='little'),
            'DEAD': int.from_bytes(status_bytes[20:22], byteorder='little'),
            'WATCH_DOG': int.from_bytes(status_bytes[22:24], byteorder='little'),
            'STEP_DIV': int.from_bytes(status_bytes[24:26], byteorder='little'),
            'STEP_MUL': int.from_bytes(status_bytes[26:28], byteorder='little'),
            'XSPEED_RES': 'Low Resolution' if (int.from_bytes(status_bytes[28:30], byteorder='little') & (1 << 15)) == (
                    1 << 15) else 'High Resolution',
            'XSPEED': int.from_bytes(status_bytes[28:30], byteorder='little') & ~(1 << 15),
            'VERSION': status_bytes[30:32]  # TODO Bytes 31 and 32 Could be integer or Binary Coded decimal
        }
