import serial

manipulator = serial.Serial('COM5', timeout=None, write_timeout=None)

# Default settings for Serial:
#
# manipulator.baudrate = 9600
# manipulator.bytesize = EIGHTBITS
# manipulator.parity = PARITY_NONE
# manipulator.stopbits = STOPBITS_ONE

_USTEPS_PER_UM_ = 25

ABSOLUTE_MODE = b'a'
RELATIVE_MODE = b'b'

HIGH_RESOLUTION = 0  # 10 uSteps/step
LOW_RESOLUTION = 1  # 50 uSteps/step


def get_current_position():
    """
    Get the micromanipulator position
    :return: A tuple of floats (x,y,z) of the position in um accurate to 0.04 um
    """
    manipulator.write(b'c\r')

    # returns 'xxxxyyyyzzzzCR' in uSteps
    position_bytes = manipulator.read(13)

    x = int.from_bytes(position_bytes[0:4], byteorder='little', signed=True)
    y = int.from_bytes(position_bytes[4:8], byteorder='little', signed=True)
    z = int.from_bytes(position_bytes[8:12], byteorder='little', signed=True)

    return float(x / _USTEPS_PER_UM_), float(y / _USTEPS_PER_UM_), float(z / _USTEPS_PER_UM_)


def go_to_position(x, y, z):
    """
    Direct the micromanipulator to a position within an accuracy of 0.04 um

    :param x: X coordinate in um
    :param y: Y coordinate in um
    :param z: Z coordinate in um
    """

    x_bytes = int(x * _USTEPS_PER_UM_).to_bytes(4, byteorder='little', signed=True)
    y_bytes = int(y * _USTEPS_PER_UM_).to_bytes(4, byteorder='little', signed=True)
    z_bytes = int(z * _USTEPS_PER_UM_).to_bytes(4, byteorder='little', signed=True)

    manipulator.write(b'm' + x_bytes + y_bytes + z_bytes + b'\r')

    # Wait for response
    manipulator.read()


def set_velocity(velocity, resolution):
    """
    Set the velocity of the manipulator. Two resolutions are available:

    HIGH_RESOLUTION allows for increments of 0.4um/second with max velocity of 13106.8 um/second
    LOW_RESOLUTION allows for increments of 2um/second with max velocity of 65534 um/second

    :param velocity: velocity value in um/second
    :param resolution: Resolution either HIGH_RESOLUTION (0.4um/second) or LOW_RESOLUTION (2um/second)
    """

    if velocity <= 0:
        raise ValueError('Velocity must be positive')

    if resolution == HIGH_RESOLUTION:
        steps = int((velocity * _USTEPS_PER_UM_) / 10)
    elif resolution == LOW_RESOLUTION:
        steps = int((velocity * _USTEPS_PER_UM_) / 50)
    else:
        raise ValueError('Use either HIGH_RESOLUTION or LOW_RESOLUTION')

    steps = (resolution << 15) | steps

    manipulator.write(b'V' + steps.to_bytes(2, 'little') + b'\r')

    # Wait for response
    manipulator.read()


def set_origin():
    """
    Sets the origin of the manipulator
    """
    manipulator.write(b'o\r')

    # Wait for response
    manipulator.read()


def refresh_display():
    """
    Refreshes the display on the manipulator
    """
    manipulator.write(b'n\r')

    # Wait for response
    manipulator.read()


def set_mode(mode):
    """
    Sets the mode of the manipulator
    :param mode: options are ABSOLUTE or RELATIVE
    """

    if mode != ABSOLUTE_MODE and mode != RELATIVE_MODE:
        raise ValueError('Use either ABSOLUTE_MODE or RELATIVE_MODE')

    manipulator.write(mode + b'\r')

    # Wait for response
    manipulator.read()


def interrupt():
    """
    Interrupts the manipulator
    """
    manipulator.write(hex(3))

    # Wait for response
    manipulator.read()


def continue_operation():
    """
    Resumes an operation on the manipulator
    """
    manipulator.write(b'e\r')

    # Wait for response
    manipulator.read()


def reset():
    """
    Resets the manipulator. No value is returned from the manipulator
    """
    manipulator.write(b'r\r')
